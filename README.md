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

```python
from tadow_api import TadowAPI, Config

app = TadowAPI(
    app_config=Config(
        debug=True,
        example_api_key="SECRET"
    )
)


```

### Custom exception handler
TadowAPI supports the creation of custom exception handlers.

Using the @app.exception_handler decorator, you can define custom behavior whenever your application raises a specific exception, such as a KeyError or a custom exception of your own.

Handlers can be implemented in the same way as regular endpoints, providing full access to the HttpRequest object and any other parameters passed to the endpoint.

By default, the application configures an http_exception_handler to handle HttpException instances raised by the internal library code. You can override this behavior by including the override=True flag in the decorator's parameters.

Note: By default, the application allows only one handler to be registered for each exception type.

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