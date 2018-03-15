#!/usr/bin/env python

# server.py: the grlc server
from flask import Flask, request, jsonify, render_template, make_response
import requests
import logging
import re
from rdflib import Graph

# grlc modules
from grlc import __version__ as grlc_version
import static as static
import gquery as gquery
import utils as utils
import pagination as pageUtils

import sparql as sparql
from queryTypes import qType

# The Flask app
app = Flask(__name__)

# Set logging format
logging.basicConfig(level=logging.DEBUG, format=static.LOG_FORMAT)
app.debug_log_format = static.LOG_FORMAT
glogger = logging.getLogger(__name__)

# Server routes
@app.route('/')
def grlcIndex():
    resp = make_response(render_template('index.html'))
    return resp

@app.route('/api/local/local/<query_name>', methods=['GET'])
def query_local(query_name):
    return query(user=None, repo=None, query_name=query_name)

@app.route('/api/<user>/<repo>/<query_name>', methods=['GET'])
@app.route('/api/<user>/<repo>/<query_name>.<extension>', methods=['GET'])
@app.route('/api/<user>/<repo>/commit/<sha>/<query_name>', methods=['GET'])
@app.route('/api/<user>/<repo>/commit/<sha>/<query_name>.<extension>', methods=['GET'])
def query(user, repo, query_name, sha=None, extension=None):
    glogger.debug("-----> Executing call name at /{}/{}/{} on commit {}".format(user, repo, query_name, sha))
    glogger.debug("Request accept header: " + request.headers["Accept"])

    loader = utils.getLoader(user, repo, sha, prov=None)

    query, q_type = loader.getTextForName(query_name)

    # Call name implemented with SPARQL query
    if q_type == qType['SPARQL']:
        raw_sparql_query = query
        raw_repo_uri = loader.getRawRepoUri()

        endpoint, auth = gquery.guess_endpoint_uri(raw_sparql_query, loader)
        if endpoint=='':
            return 'No SPARQL endpoint indicated', 407

        glogger.debug("=====================================================")
        glogger.debug("Sending query to SPARQL endpoint: {}".format(endpoint))
        glogger.debug("=====================================================")

        query_metadata = gquery.get_metadata(raw_sparql_query)

        pagination = query_metadata['pagination'] if 'pagination' in query_metadata else ""

        # Rewrite query using parameter values
        rewritten_query = gquery.rewrite_query(raw_sparql_query, request.args, endpoint)

        # Rewrite query using pagination
        paginated_query = gquery.paginate_query(rewritten_query, request.args)

        resp = None
        # If we have a mime field, we load the remote dump and query it locally
        if 'mime' in query_metadata and query_metadata['mime']:
            g = Graph()
            try:
                g.parse(endpoint, format=query_metadata['mime'])
            except Exception as e:
                glogger.error(e)
            results = g.query(paginated_query, result='sparql')
            # Prepare return format as requested
            resp_string = ""

            if 'application/json' in request.headers['Accept'] or (extension and 'application/json' in static.mimetypes[extension]):
                resp_string = results.serialize(format='json')
            elif 'text/csv' in request.headers['Accept'] or (extension and 'text/csv' in static.mimetypes[extension]):
                resp_string = results.serialize(format='csv')
            else:
                return 'Unacceptable requested format', 415
            del g

            resp = make_response(resp_string)
        # If there's no mime type, the endpoint is an actual SPARQL endpoint
        else:
            if extension:
                returnFormat = sparql.selectExtensionFormat(extension)
            else:
                returnFormat = sparql.selectReturnFormat(request.headers['Accept'])
            response = sparql.executeSPARQLQuery(endpoint, paginated_query, returnFormat)

            # Response headers
            resp = make_response(response.text)
            resp.headers['Server'] = 'grlc/' + grlc_version
            resp.headers['Content-Type'] = response.headers['Content-Type']

        # If the query is paginated, set link HTTP headers
        if pagination:
            # Get number of total results
            count = gquery.count_query_results(rewritten_query, endpoint)
            headerLink =  pageUtils.buildPaginationHeader(count, pagination)
            resp.headers['Link'] = headerLink

        return resp
    # Call name implemented with TPF query
    elif q_type == qType['TPF']:
        raw_tpf_query = query
        endpoint, auth = gquery.guess_endpoint_uri(raw_tpf_query, raw_repo_uri)
        glogger.debug("=====================================================")
        glogger.debug("Sending query to TPF endpoint: {}".format(endpoint))
        glogger.debug("=====================================================")

        query_metadata = gquery.get_yaml_decorators(raw_tpf_query)

        # TODO: pagination for TPF

        # Preapre HTTP request
        headers = { 'Accept' : request.headers['Accept'] , 'Authorization': 'token {}'.format(static.ACCESS_TOKEN)}
        if extension:
            headers = { 'Accept' : static.mimetypes[extension] , 'Authorization': 'token {}'.format(static.ACCESS_TOKEN)}
        tpf_list = re.split('\n|=', raw_tpf_query)
        subject = tpf_list[tpf_list.index('subject') + 1]
        predicate = tpf_list[tpf_list.index('predicate') + 1]
        object = tpf_list[tpf_list.index('object') + 1]
        data = { 'subject' : subject, 'predicate' : predicate, 'object' : object}

        response = requests.get(endpoint, params=data, headers=headers, auth=auth)
        glogger.debug('Response header from endpoint: ' + response.headers['Content-Type'])

        # Response headers
        resp = make_response(response.text)
        resp.headers['Server'] = 'grlc/' + grlc_version
        resp.headers['Content-Type'] = response.headers['Content-Type']

        return resp
    else:
        return "Couldn't find a SPARQL, RDF dump, or TPF query with the requested name", 404


@app.route('/api/local', methods=['GET'])
def api_docs_local():
    return api_docs(user='local', repo='local', sha=None)

@app.route('/api/local/local/spec', methods=['GET'])
def swagger_spec_local():
    return swagger_spec(user=None, repo=None, sha=None, content=None)

@app.route('/api/<user>/<repo>', strict_slashes=False)
@app.route('/api/<user>/<repo>/api-docs')
@app.route('/api/<user>/<repo>/commit/<sha>')
@app.route('/api/<user>/<repo>/commit/<sha>/api-docs')
def api_docs(user, repo, sha=None):
    return render_template('api-docs.html', user=user, repo=repo, sha=sha)

@app.route('/api/<user>/<repo>/spec', methods=['GET'])
@app.route('/api/<user>/<repo>/commit/<sha>/spec')
def swagger_spec(user, repo, sha=None, content=None):
    glogger.info("-----> Generating swagger spec for /{}/{} on commit {}".format(user,repo,sha))

    swag = utils.build_swagger_spec(user, repo, sha, static.SERVER_NAME)

    resp_spec = make_response(jsonify(swag))

    resp_spec.headers['Content-Type'] = 'application/json'

    resp_spec.headers['Cache-Control'] = static.CACHE_CONTROL_POLICY # Caching JSON specs for 15 minutes

    glogger.info("-----> API spec generation for /{}/{} on commit {} complete".format(user, repo, sha))

    return resp_spec

if __name__ == '__main__':
    app.run(host=static.DEFAULT_HOST, port=static.DEFAULT_PORT, debug=True)
