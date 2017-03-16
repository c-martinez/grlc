<p algin="center"><img src="https://raw.githubusercontent.com/CLARIAH/grlc/master/src/static/grlc_logo_01.png" width="250px"></p>

[![Join the chat at https://gitter.im/grlc](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/grlc/Lobby#)

grlc, the <b>g</b>it <b>r</b>epository <b>l</b>inked data API <b>c</b>onstructor, automatically builds Web APIs using SPARQL queries stored in git repositories. http://grlc.io/

**Contributors:**	[Albert Meroño](https://github.com/albertmeronyo), [Rinke Hoekstra](https://github.com/RinkeHoekstra), [Carlos Martínez](https://github.com/c-martinez)

**Copyright:**	Albert Meroño, VU University Amsterdam  
**License:**	MIT License (see [LICENSE.txt](LICENSE.txt))

## Install and run

Running via [docker](https://www.docker.com/) is the easiest and preferred form of deploying grlc. You'll need a working installation of [docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/). To deploy grlc, just pull the latest image from Docker hub, and run docker compose with a `docker-compose.yml` that suits your needs (an [example](docker-compose.default.yml) is provided in the root directory):

<pre>
git clone https://github.com/CLARIAH/grlc
cd grlc
docker pull clariah/grlc
docker-compose -f docker-compose.default.yml up
</pre>

(You can omit the first two commands if you just copy [this file](docker-compose.default.yml) somehwere in your filesystem)
If you use the supplied `docker-compose.default.yml` your grlc instance will be available at http://localhost:8001

### Alternative install methods

Through these you'll miss some cool docker bundled features (like nginx-based caching). We provide these alternatives just for testing, development scenarios, or docker compatibility reasons.

#### pip

If you want to use grlc as a library, you'll find it useful to install via `pip`.

<pre>
pip install grlc
grlc-server
</pre>

More details can be found at [grlc's PyPi page](https://pypi.python.org/pypi/grlc/1.0) (thanks to [c-martinez](https://github.com/c-martinez)!).

#### Flask application

 you can find an example of how to run grlc natively [here](https://github.com/CLARIAH/grlc/blob/master/docker-build/entrypoint.sh#L20)

## Usage

grlc assumes a GitHub repository (support for general git repos is on the way) where you store your SPARQL queries as .rq files (like in [this one](https://github.com/CEDAR-project/Queries)). grlc will create an API operation per such a SPARQL query/.rq file.

If you're seeing this, your grlc instance is up and running, and ready to build APIs. Assuming you got it running at <code>http://localhost:8088/</code> and your queries are at <code>https://github.com/CEDAR-project/Queries</code>, just point your browser to the following locations:

- To request the swagger spec of your API, <code>http://localhost:8088/api/username/repo/spec</code>, e.g. [http://localhost:8088/api/CEDAR-project/Queries/spec](http://localhost:8088/api/CEDAR-project/Queries/spec) or [http://localhost:8088/api/CLARIAH/wp4-queries/spec](http://localhost:8088/api/CLARIAH/wp4-queries/spec)
- To request the api-docs of your API swagger-ui style, <code>http://localhost:8088/api/username/repo/api-docs</code>, e.g. [http://localhost:8088/api/CEDAR-project/Queries/api-docs](http://localhost:8088/api/CEDAR-project/Queries/api-docs) or [http://localhost:8088/api/CLARIAH/wp4-queries/api-docs](http://localhost:8088/api/CLARIAH/wp4-queries/api-docs)

By default grlc will direct your queries to the DBPedia SPARQL endpoint. To change this either:

* Add a `endpoint:` decorator in the first comment block of the query text (preferred, see below)
* Add the URL of the endpoint on a single line in an `endpoint.txt` file within the GitHub repository that contains the queries.
* Or you can directly modify the grlc source code (but it's nicer if the queries are self-contained)

That's it!

### Example APIs

Check these out:

- http://grlc.io/api/CLARIAH/wp4-queries/
- http://grlc.io/api/albertmeronyo/lodapi/
- http://grlc.io/api/albertmeronyo/lsq-api

## Decorator syntax
A couple of SPARQL comment embedded decorators are available to make your swagger-ui look nicer (note all comments start with <code>#+ </code>):

- To specify a query-specific endpoint, <code>#+ endpoint: http://example.com/sparql</code>.
- To indicate the HTTP request method, <code>#+ method: GET</code>.
- To paginate the results in e.g. groups of 100, <code>#+ pagination: 100</code>.
- To create a summary of your query/operation, <code>#+ summary: This is the summary of my query/operation</code>
- To assign tags to your query/operation,
    <pre>&#35;+ tags:
  &#35;+   - firstTag
  &#35;+   - secondTag</pre>
- To indicate which parameters of your query/operation should get enumerations (and get dropdown menus in the swagger-ui),
    <pre>&#35;+ enumerate:
  &#35;+   - var1
  &#35;+   - var2</pre>

  Notice that these should be plain variable names without SPARQL/BASIL conventions (so `var1` instead of `?_var1_iri`)

See examples at [https://github.com/albertmeronyo/lodapi](https://github.com/albertmeronyo/lodapi).

## Features

- Request parameter mappings into SPARQL: grlc is compliant with [BASIL's convention](https://github.com/the-open-university/basil/wiki/SPARQL-variable-name-convention-for-WEB-API-parameters-mapping) on how to map GET/POST request parameters into SPARQL
- Automatic, user customizable population of parameter values in swagger-ui's dropdown menus via SPARQL triple pattern querying
- URL-based content negotiation: you can request for specific content types by attaching them to the operation request URL, e.g. [http://localhost:8088/CEDAR-project/Queries/residenceStatus_all.csv](http://localhost:8088/CEDAR-project/Queries/residenceStatus_all.csv) will request for results in CSV
- Pagination of API results, as per the `pagination` decorator and [GitHub's API Pagination Traversal](https://developer.github.com/guides/traversing-with-pagination/)
- Docker images in Docker Hub for easy deployment
- Compatibility with [Linked Data Fragments](http://linkeddatafragments.org/) servers, RDF dumps, and HTML+RDFa files
