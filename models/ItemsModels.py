from pydantic import BaseModel, Field
from typing import Union

# Creamos un modelo para nuestros datos
class Item( BaseModel ):
    # Ponemos los campos, si lo usamos en la peticion post entonces este sera la estructura de los datos
    name:str = Field(title='Nombre para el item', max_length=5 ) # Usamos Field de pydantic para metados
    description: Union[str, None] = None # Valor por defecto, este valor es opcional en el body
    price: float
    tax: Union[ float, None ] = None # Valor por defecto es None, este valor es opcional en el body

    
class User( BaseModel ):
    username: str
    full_name: Union[str, None] = None

