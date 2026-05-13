## Invernadero Virtual

# asignatura:
Implementa base de datos no relacionales
# profe:
treviño Tapia Juan Ruben
# Fecha:
13/05/26


# integrantes:
**Maria Luz Ubiarco Montes 3D** ,
**Oscar Adrian Medina Hernandez 3D**

# foto:
![WhatsApp Image 2025-09-23 at 9 08 04 AM (1)](https://github.com/user-attachments/assets/e41c28b6-6f73-4965-9d85-53e7ba798e0e) ![MHOA (1)](https://github.com/user-attachments/assets/b293f166-2e0c-45e1-9648-9541779cc4cf)


# Descripción del Proyecto
Invernadero Virtual es una página web que pensamos y queremos desarrollar para que la gente   pueda consultar información real sobre plantas y flores de una forma fácil y pueda agregar a favoritos la planta que le guste. La idea nació porque mucha gente compra plantas porque se ven bonitas, pero se les terminan muriendo pronto porque no saben que cuidados necesitan realmente, como la cantidad de agua o el tipo de luz.
# objetivo
En esta aplicación, el usuario no solo lee información, sino que sienta que tiene su propio espacio digital. por eso, diseñaremos un sistema donde pueden hacerse una cuenta, inicie sesión y guardar las plantas que más les gusten en una lista de favoritos.
#Problema que resuelve :
El problema principal es que la información sobre botánica a veces está muy dispersa o es difícil de entender. Con "Invernadero Virtual" resolvemos esto centralizando todo en un solo 
lugar. Ayudamos a evitar que las plantas se mueran por falta de conocimiento, ofreciendo guías claras sobre riego, luz y cuidados básicos en una plataforma visual y sencilla.  

# Estructura de la Base de Datos (MongoDB)
Nuestro objetivo es armar una base de datos en MongoDB que funcione bien para nuestra página de plantas. Queremos que la base de datos sea capaz de guardar toda la información de los cuidados de las plantas y que también sepa diferenciar entre un usuario normal y un administrador. Lo más importante es lograr que cuando un usuario guarde una planta en sus favoritos, esa información se quede bien registrada en Mongo para que no se pierda al cerrar sesión.

Listado de Colecciones (Estructura de MongoDB)
Nuestra base de datos tendrá estas tres colecciones:
Colección usuarios: Aquí guardaremos a las personas que se registren.
Campos principales: Nombre de usuario, correo, contraseña (encriptada) y el rol (para saber si es usuario normal o admin).
Colección plantas: Será nuestro catálogo principal.
Campos principales: Nombre de la planta, descripción, cuidados (riego/luz), categoría y el enlace de la imagen.


Colección favoritos: Esta es la que conecta a las otras dos.
Campos principales: El ID del usuario y el ID de la planta que guardó. Así, cuando el usuario entre, Mongo busca en esta
lista qué plantas le pertenecen a él.
