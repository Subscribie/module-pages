### Pages Module

Ability to add pages to shop via admin dashboard.

Reference user story: https://github.com/Subscribie/subscribie/issues/121


## Usage

TODO: Ability to add and edit pages from the admin dashboard.

In the background, jamla.yaml stores pages in the following way:

```
pages:
- <page-name>:
    path: <path>
    template_file: <filename>.html
```

Example:

```
pages:
- privacy:
    path: privacy
    template_file: privacy.html
- demo:
    path: demo
    template_file: demo.html
```
