# tadowAPI
<p align="center">
    <img src="tadowAPI.png">
</p>




## Installation

```
pip install tadow_api
```

Support XML parsing
```
pip install tadow_api[xml]  #TODO 
```

## Features

- [Validation](#validation)
- [Router](#router)
- [Cookies](#cookies)
- [Config](#config-file)
- [Exception handler](#custom-exception-handler)

### Sample app


```python
from tadow_api import TadowAPI

app = TadowAPI()


@app.route(path="/")
async def index():
    return "Index page"


@app.route(path="/items")
def items_list(request):
    return {"http_method": request.http_method}
```

### Validation
```python
from tadow_api import TadowAPI
from pydantic import BaseModel

app = TadowAPI()


class CreateItem(BaseModel):
    name: str
    price: float
    
class ItemResponse(CreateItem):
    id: str


@app.route("/", response_model=list[ItemResponse])
def get_items():
    return [
        ItemResponse(id=1, name="Test", price=20.00),
        ItemResponse(id=2, name="Test2", price=10.00)
    ]
    

@app.route(
    path="/items",
    methods=["POST"], 
    request_model=CreateItem, 
    response_model=ItemResponse
)
def create_items(request):
    item: CreateItem = request.data
    # PERFORM CREATE
    return {
        "id": 1,
        "name": "Example",
        "price": 20.00
    }, 201
```

### Router

```python
# items.py
from tadow_api.routing import Router

router = Router(prefix="/items")

@router.route(path="/", methods=["GET", "POST"])
def get_list_or_create_item(request):
    if request.http_method == "POST":
        # ... PERFORM CREATE ...
        return {}, 201
    else:
        # ... PERFORM GET ...
        return {}, 200
```


```python
# main.py
from tadow_api import TadowAPI
from items import router as items_router

app = TadowAPI()
app.register_router(router=items_router)
```

### Cookies


Accessing cookies
```python

@app.route(path="/index")
def index(request):
    print(request.cookies)
    return {}
```

Setting cookies
```python
from tadow_api.requests import Cookie
...

@app.route(path="/index")
def index(request):
    return {}, None, [Cookie(
        name="CustomCookie", 
        value="Example",
    )
    ]


```

### Config file

Similar to other frameworks, you can manage your application configuration by creating a Config (Settings) instance.

By default, the Config class configures the following fields:

- `debug` – Enables the debugger and includes traceback details in the HttpResponse.
- `default_content_type` – Configures the default content type when it is not included in the request.
- `default_encoding` – Sets the default encoding for request and response content.

[!NOTE] You can add custom fields to the configuration, making them easily accessible across your entire codebase.

```python
# main.py
from tadow_api import TadowAPI, Config
from tadow_api.config import app_config

app = TadowAPI(
    config=Config(
        debug=True,
        example_api_key="SECRET"
    )
)


@app.route("/")
def index():
    return {"example_api_key": app_config().example_api_key}
```


### Custom exception handler
TadowAPI supports the creation of custom exception handlers.

Using the `@app.exception_handler` decorator, you can define custom behavior whenever your application raises a specific exception, such as a `KeyError` or a custom exception of your own.

Handlers can be implemented in the same way as regular endpoints, providing full access to the HttpRequest object and any other parameters passed to the endpoint.

[!NOTE] The application configures an http_exception_handler to handle HttpException instances raised by the internal library code. You can override this behavior by including the `override=True` flag in the decorator's parameters.

[!NOTE] The application allows only one handler to be registered for each exception type.

Example:
```python
from tadow_api import TadowAPI

app = TadowAPI()

@app.exception_handler(KeyError)
async def async_exception_handler(exception: KeyError, request: "HttpRequest"):
    # ... Async handler code ...
    
@app.exception_handler(ValueError)
def sync_exception_handler(exception: KeyError, request: "HttpRequest"):
    # ... Sync handler code ...

```


## Coming soon

- Dev command with hot reload
- Class based views
- Test client