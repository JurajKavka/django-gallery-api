# Gallery API

This is very simple gallery app that provides only JSON API for creating gallery, adding, removing images and getting image thumbnails of specified sizes.

Administration of the galleries can be also done from standard Django admin interface.

It is written in Django 3.0, with Django REST framework.

> **NOTE: This project is only for presentation purposes! Don't use it nowhere!**

## Running the project in local enviroment

### docker-compose

The most convenient way, how to run this project is to use *Docker* with [`docker-compose`](https://docs.docker.com/compose/install/) tool.

In project directory (where you see `docker-compose.yml`) run commad:
```shell
docker-compose up
```
Building the image takes quite a long time. When the container is running, local server is listening on port `8000` and app is accessible on [`http://localhost:8000`](http://localhost:8000).

### Docker
If you don't have `docker-compose`, you can use standard Docker command to build image and run container. Those commands are part of `Makefile`.

```shell
make build
make run
```

Clean container and image with
```shell
make clean
```

### The pure Python way (without Docker)
To run this project without docker You will need to have installed:

- python 3
- [`pipenv`](https://github.com/pypa/pipenv)
- sqlite 3

In `src/` subdirectory directory (where you see `Pipfile`) run command:

```shell
pipenv --three install
```

Now, you need to run local development server with

```
pipenv run python manage.py runserver
```

Try running app in browser on url [`http://localhost:8000/`](http://localhost:8000/).

> **NOTE**: This project depends on `Pillow` library, which can be difficult to install for a first time, because `Pillow` depends on external packages which must be installed globally in your operating system. For more details, reffer [Pillow installation guide](https://pillow.readthedocs.io/en/stable/installation.html).

### Testing the API
On `http://localhost:8000/` is API schema with all the links and details. 

In a nutshell:

- `/gallery` - list of the galleries or create one, providing `name` in request body
- `/gallery/{path}` - detail of the gallery with all the images. `POST` method to this endpoint is used to upload images to selected gallery. You can upload several images in one request. `DELETE` method deletes gallery with all the images and generated thumbnails. When you use `fullpath` of the image as a `path` parameter of this request, server returns original image. `DELETE` method combined with `fullpath` of the image removes image from gallery.
- `images/{x_size}x{y_size}/{gallery_path}/{image_path}/` - returns resized image. Image is defined by `{gallery_path}/{image_path}`, but it is same as a `fullpath` attribude from the detail of image. The resizing method does not maintain aspect ratio, only when one of the `size` parameter is `0`.

You can also try those links from browser, for example:

- `http://localhost:8000/gallery`

Django REST framework will render its own views for those endpoints.

> **NOTE: API endpoints are not authorized! Authentication and authorization is explicitely disabled for the simplicity of project presentation!**

### Administration from backend (Django Admin)
This Django project comes with prepopulated sqlite database in file `src/db.sqlite3`. This allows without any special effort run the project and use. You can administrace application from standard Django admin on url `http://localhost:8000/admin`. 

Default superuser is:

- name: `admin`
- password:`admin123`
