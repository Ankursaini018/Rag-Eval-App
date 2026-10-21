```markdown
# Day 6: 10 questions through the baseline pipeline

Run on 2026-10-20 (top 5 chunks, prompt v1, no tuning).

## 1. How do I declare a path parameter in FastAPI?

**Answer:** To declare a path parameter in FastAPI, add a function argument that matches a placeholder in the route path and give it a type annotation. FastAPI will automatically parse the value from the URL and pass it to the function. For example:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

Here `item_id` is a path parameter declared with the type `int` (you could use `str`, `float`, etc.). The value is extracted from the URL segment that matches `{item_id}` and converted to the specified type before being passed to the function. [1]

- Refused: no
- Cited: path-params.md p1
- Retrieved (doc page, score): path-params.md p1 (0.85); path-params-numeric-validations.md p1 (0.82); body.md p3 (0.80); path-operation-configuration.md p1 (0.79); body-multiple-params.md p1 (0.79)
- **Verdict:** [x] correct [ ] weak [ ] wrong
- Why: The answer directly explains the documented FastAPI mechanism for declaring a path parameter, including the matching route placeholder and type annotation. The retrieved `path-params.md` result has the highest score and directly supports the answer.

## 2. How do I make a query parameter optional?

**Answer:** To make a query parameter optional, give it a default value of `None`.

For example:

```python
def read_items(q: str | None = None):
    ...
```

This tells FastAPI that the parameter `q` is optional and will be `None` if not supplied in the URL.

[2]

- Refused: no
- Cited: query-params.md p1
- Retrieved (doc page, score): query-params.md p2 (0.83); query-params.md p1 (0.81); query-params-str-validations.md p4 (0.77); query-params-str-validations.md p5 (0.76); query-params-str-validations.md p2 (0.73)
- **Verdict:** [x] correct [ ] weak [ ] wrong
- Why: The answer correctly describes the documented pattern of using `None` as the default value for an optional query parameter. The retrieved query-parameter documentation directly supports this.

## 3. How do I set the status code returned by a path operation?

**Answer:** Use the `status_code` parameter on the path-operation decorator (e.g., `@app.get(..., status_code=201)`). This tells FastAPI to return that HTTP status code and to document it in the OpenAPI schema. [1] [2]

- Refused: no
- Cited: path-operation-configuration.md p1, response-status-code.md p1
- Retrieved (doc page, score): path-operation-configuration.md p1 (0.84); response-status-code.md p1 (0.77); response-status-code.md p2 (0.73); path-params.md p1 (0.73); bigger-applications.md p2 (0.72)
- **Verdict:** [x] correct [ ] weak [ ] wrong
- Why: The answer identifies the `status_code` argument on the path-operation decorator and explains its purpose. Both cited documents directly support the answer.

## 4. How can I limit the maximum length of a query parameter?

**Answer:** Use FastAPI’s `Query` (or `Annotated` with `Query`) and set the `max_length` argument.

For example:

```python
q: str | None = Query(default=None, max_length=50)
```

This validates that the query string is no longer than 50 characters, shows a clear error if it isn’t, and documents the limit in the OpenAPI schema. [1]

- Refused: no
- Cited: query-params-str-validations.md p2
- Retrieved (doc page, score): query-params-str-validations.md p2 (0.79); query-params.md p1 (0.76); query-params.md p2 (0.75); query-param-models.md p1 (0.74); query-params-str-validations.md p5 (0.74)
- **Verdict:** [x] correct [ ] weak [ ] wrong
- Why: The answer gives the documented `Query(..., max_length=...)` validation mechanism and provides a valid example. The highest-scoring retrieved document directly covers query-string validation.

## 5. How can I run some code after returning a response, without making the client wait?

**Answer:** Use FastAPI’s **BackgroundTasks**.

Define a function that does the work you want to run after the response, then add it to the `BackgroundTasks` object in your path-operation function with `.add_task()`. The task will execute after the response is sent, so the client does not wait for it. [1]

- Refused: no
- Cited: background-tasks.md p1
- Retrieved (doc page, score): background-tasks.md p1 (0.73); stream-json-lines.md p2 (0.73); handling-errors.md p3 (0.73); handling-errors.md p1 (0.72); response-model.md p1 (0.71)
- **Verdict:** [x] correct [ ] weak [ ] wrong
- Why: The answer directly identifies `BackgroundTasks` and explains the relevant `.add_task()` mechanism. `background-tasks.md` is the highest-scoring and directly relevant retrieved document.

## 6. At what URL can I see the automatic interactive API documentation?

**Answer:** The automatic interactive API documentation is available at **http://127.0.0.1:8000/docs**. [2]

- Refused: no
- Cited: first-steps.md p3
- Retrieved (doc page, score): metadata.md p1 (0.72); first-steps.md p3 (0.69); bigger-applications.md p7 (0.69); schema-extra-example.md p2 (0.68); schema-extra-example.md p3 (0.66)
- **Verdict:** [x] correct [ ] weak [ ] wrong
- Why: The answer gives the standard interactive documentation URL shown in the retrieved FastAPI documentation. `first-steps.md p3` directly supports the `/docs` endpoint.

## 7. How do I use a path parameter and a request body in the same endpoint?

**Answer:** You can declare a path parameter and a request body in the same path-operation function.

Define the path parameter in the route path and type-annotate it normally (e.g. `int`, `str`).

Define the body parameter as a Pydantic model (or use `Body(...)` for singular values).

FastAPI will read the path value from the URL, parse and validate the body from the request payload, and pass both to the function.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/{item_id}")
def update_item(item_id: int, item: Item):
    # item_id comes from the path
    # item comes from the JSON body
    return {"item_id": item_id, "item": item}
```

In this example, `item_id` is taken from the URL (`/items/42`), while `item` is parsed from the JSON body. FastAPI automatically handles parsing, validation, and documentation for both parameters.

- Refused: no
- Cited: none
- Retrieved (doc page, score): body-multiple-params.md p1 (0.80); path-params.md p1 (0.77); body.md p1 (0.77); body.md p3 (0.74); first-steps.md p5 (0.74)
- **Verdict:** [x] correct [ ] weak [ ] wrong
- Why: The retrieved documents strongly support the combination of path parameters and request-body parameters. The example correctly separates the path value from the Pydantic request body.

## 8. How can I control which websites in a browser are allowed to call my API?

**Answer:** You control which websites (origins) are allowed to call your API by configuring the **CORS** middleware in your FastAPI application.

Add a list of allowed origins to the `allow_origins` parameter of `CORSMiddleware`. Only requests coming from those origins will receive the appropriate CORS headers and be permitted by the browser.

- In the FastAPI app you can do:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- The `allow_origins` list can also be set to `["*"]` to allow all origins, but this will not work if `allow_credentials` is `True` (see the restriction in the documentation).

This configuration is described in the CORS section of the documentation and the list of supported arguments for `CORSMiddleware` [1][2].

- Refused: no
- Cited: cors.md p1, cors.md p2
- Retrieved (doc page, score): cors.md p1 (0.71); cors.md p2 (0.70); bigger-applications.md p7 (0.67); metadata.md p1 (0.66); bigger-applications.md p2 (0.66)
- **Verdict:** [x] correct [ ] weak [ ] wrong
- Why: The answer correctly identifies `CORSMiddleware` and `allow_origins` as the mechanism for configuring browser origins. The retrieved CORS documents directly support the configuration shown.

## 9. What is the capital city of France?

**Answer:** I don't know based on the provided documents.

- Refused: yes
- Cited: none
- Retrieved (doc page, score): cookie-param-models.md p2 (0.43); response-status-code.md p2 (0.39); first-steps.md p2 (0.39); header-params.md p1 (0.39); index.md p2 (0.39)
- **Verdict:** [x] correct [ ] weak [ ] wrong
- Why: The question is outside the provided FastAPI documentation. The retrieved documents have low relevance scores and do not provide evidence for the answer, so refusing rather than introducing unsupported information is the correct behavior for a document-grounded RAG system.

## 10. How do I train a PyTorch neural network inside a FastAPI endpoint?

**Answer:** I don't know based on the provided documents.

- Refused: yes
- Cited: none
- Retrieved (doc page, score): first-steps.md p1 (0.66); index.md p1 (0.65); testing.md p2 (0.64); testing.md p1 (0.64); cookie-param-models.md p2 (0.63)
- **Verdict:** [x] correct [ ] weak [ ] wrong
- Why: The retrieved documents do not provide evidence about training a PyTorch neural network inside a FastAPI endpoint. Refusing to answer is therefore appropriate for the document-grounded baseline rather than generating unsupported information.
```