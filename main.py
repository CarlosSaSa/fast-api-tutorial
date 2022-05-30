from fastapi import FastAPI, status, Response, HTTPException, Query, Path, Body
from typing import Union

from models.ItemsModels import Item, User

# Creamos una instancia de FastAPI
app = FastAPI( debug=True, openapi_url=None )

# Elementos de una lista en memeoria
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

# Creamos una ruta de ejemplo, esto es la ruta inicial
@app.get("/", status_code=status.HTTP_200_OK ) # Poniendo asi el codigo de respuesta este siempre devolverá el 200
def read_root():
    return { "Mensaje": "Raiz de la ruta", "estado": True }

# Ruta con parametros
@app.get("/some-parameter/{edad}", status_code= status.HTTP_200_OK )
def some_parameter( edad: str, response: Response ):
    if not str( edad ).isnumeric():
        raise HTTPException( status_code= status.HTTP_400_BAD_REQUEST, detail='Valor no permitido' )
    edad = int(edad)
    if edad >= 18:
        return { "Mensaje": "Eres mayor de edad", "estado": True, "edad": edad }
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return { "Mensaje": "No puede pasar porque no eres mayot de edad", "estado": False, "edad": edad }

# Ruta que tiene un parametro 
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
    # Si nuestra ruta seria la siguiente: files//home/johndoe/myfile.txt esto podria interpretarse que la variable file_path es una cadena de una ruta y mas no una ruta de api

# Ruta para query parameters
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 20): 
    # Para declarar y obtener los querys params podemos declararlos dentro de la funcion, los querys params son skipo y limit 
    # Normalmente estos parametros son strings pero cuando se declaran con tipo se hacen las validaciones como el parseo, validacion y documentación
    # Si nosotros ponemos las rutas sin parametros y nuestros query params en la función sin valores predeterminados ( se hacen obligatorios ) entonces nos marca un error
    return fake_items_db[skip : skip + limit]

# Podemos hacer la unión de tipos
# @app.get("/items/{item_id}")
# async def read_item(item_id: str, q: Union[str, None] = None):
#     if q:
#         return {"item_id": item_id, "q": q}
#     return {"item_id": item_id}

# Metodo para hacer un post
@app.post('/items', status_code= status.HTTP_200_OK)
def create_item( item: Item): # Como es una peticion post entonces en el body podemos recibir un json con la estructura de una clase llamada Item
    # Revisamos los datos
    # name = item.name.upper()
    # print('Name: ', name ) 

    # Podemos convertir nuestro modelo a un diccionario
    # print('Item: ', item, type( item ) ) # Es como una instancia de nuestra clase
    # print('Item to dict, ', item.dict(), type( item.dict() )) # Es un diccionario
    return item

# Metodo post con body y parametros variables
@app.put("/items/{item_id}") # Declaramos un path variable
def create_item(item_id: int, item: Item): # Se reconoce automaticamente cual es el path variable y cual el modelo del body, el orden no importa
    return {"item_id": item_id, **item.dict()}


# @app.put("/test/items/{item_id}") # Recibe un  path variable
# async def create_item(item_id: int, item: Item, q: Union[str, None] = None): 
#     # Podemos decir lo siguiente de la documentación:
#     """
#         El query param llamado 'p' se hace opcional si tiene un valor por defecto
#         Si el parámetro también se declara en la ruta, se utilizará como parámetro de ruta.
#         Si el parámetro es de un tipo singular (como int, float, str, bool, etc.) se interpretará como un parámetro de consulta.
#         Si se declara que el parámetro es del tipo de un modelo Pydantic, se interpretará como un cuerpo de solicitud.
#     """
#     result = {"item_id": item_id, **item.dict()}
#     if q:
#         result.update({"q": q})
#     return result

# Podemos agreagr metadatos cuando se trata de un query params
@app.put("/test/items/{item_id}") # Recibe un  path variable
async def create_item( *, # Con este operador podemos definir el orden de nuestros parametros, sin importar cuales sean obligatorios u opcionales
                      item_id: int = Path( title='Path variable para obtener el id' ),
                      item: Item, 
                      q: Union[str, None] = Query( default=None,  
                                                   title='Parametro de consulta Q', 
                                                   description='Parametro de consulta para obtener información',
                                                   alias= 'item-query')): # Con el alias indicamos que nuestro query params en la URL será item-query y se mapea a la variable q -> http://127.0.0.1:8000/items/?item-query=foobaritems

    # Podemos decir lo siguiente de la documentación:
    """
        El query param llamado 'p' se hace opcional si tiene un valor por defecto
        Si el parámetro también se declara en la ruta, se utilizará como parámetro de ruta.
        Si el parámetro es de un tipo singular (como int, float, str, bool, etc.) se interpretará como un parámetro de consulta.
        Si se declara que el parámetro es del tipo de un modelo Pydantic, se interpretará como un cuerpo de solicitud.
    """
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result

# Multiples bodys, en realidad es un solo json pero con dos claves que envuelven los modelos json
@app.put("/multiple/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    """ Se usará los nombres de los parametros como claves en el body y se espera un formato como el siguiente:
        {
            "item": {
                "name": "Foo",
                "description": "The pretender",
                "price": 42.0,
                "tax": 3.2
            },
            "user": {
                "username": "dave",
                "full_name": "Dave Grohl"
            }
        }
     """
    # Se hará la conversión automatica de la request, de modo que las variables de tipo de modelo de pydantic se asociaen con sus valores correspondientes
    results = {"item_id": item_id, "item": item, "user": user}
    return results

@app.put("/add-body/items/{item_id}")
async def update_item(item_id: int, # Path variable
                      item: Item, # Elemento del body
                      user: User, # Elemento del body
                      importance: int = Body(), # Parametros que es incluido dentro del body
                      q: Union[str, None] = None): # Query params
    """
        Si observamos nuestros parametros de función estamos usando una variable llamada importance y con esto indicamos que no es un query params
        si no que es otra clave que viene del body, es decir, como sabemos nuestro body estará compuesto de tres claves, item, user e importance
        {
            "item": {
                "name": "Foo",
                "description": "The pretender",
                "price": 42.0,
                "tax": 3.2
            },
            "user": {
                "username": "dave",
                "full_name": "Dave Grohl"
            },
            "importance": 5
        }

    """
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results

