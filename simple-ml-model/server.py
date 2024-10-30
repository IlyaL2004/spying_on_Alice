from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import uvicorn
import pandas as pd
import joblib
import io
from scipy.sparse import csr_matrix


app = FastAPI(
    title="Simple model"
)
model = joblib.load("./model.joblib")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    
    # read data for prediction
    X = pd.read_csv(io.BytesIO(contents))

    # transform data for prediction 
    times = ["time%s" % i for i in range(1, 11)]
    sites = ["site%s" % i for i in range(1, 11)]
    
    X[times] = X[times].apply(pd.to_datetime)

    full_sites = X[sites]
    sites_flatten = full_sites.values.flatten()
    full_sites_sparse = csr_matrix(
        (
            [1] * sites_flatten.shape[0],
            sites_flatten,
            range(0, sites_flatten.shape[0] + 10, 10),
        )
    )[:, 1:]

    X = full_sites_sparse


    # get prediction
    y = pd.DataFrame(model.predict(X))
    
    # send it out
    output = io.StringIO()
    y.to_csv(output, index=False)
    output.seek(0) 

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=prediction.csv"},
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=80)