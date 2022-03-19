# Commands Example

######

- httpc help
- httpc help get
- httpc help post
- httpc get 'http://httpbin.org/get?course=networking&assignment=1%27'
- httpc get -v 'http://httpbin.org/get?course=networking&assignment=1%27'
- httpc post -h Content-Type:application/json -d '{"Assignment": 1}' http://httpbin.org/post
- httpc post -h Content-Type:application/json -f 'local/http_body1.txt' http://httpbin.org/post

- alias httpc='python /c/Users/break/Desktop/http_server/client.py'
- alias httpfs='python /c/Users/break/Desktop/http_server/client_file_system.py'

## Dummy request for 301 redirect

- httpc get https://run.mocky.io/v3/306d1f48-02cf-4ad6-a216-65cb6a40ad95
- httpc get -v https://run.mocky.io/v3/306d1f48-02cf-4ad6-a216-65cb6a40ad95
- httpc get -o local/response.txt -v 'http://httpbin.org/get?course=networking&assignment=1%27'

## Requests for file system

- httpfs get -d 'asdf'
- httpfs get -d 'local'
- httpfs get -d 'local/http_body1.txt'
- httpfs get -v -d 'local/http_body1.txt'
- httpfs post -d 'test.txt' --body 'my name is not JoJo'
- httpfs post -d '../../test.txt' --body 'my name is not JoJo'
