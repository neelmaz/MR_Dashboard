"""
FastAPI Backend - Handles data processing and API endpoints
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import json
from data_loader import get_loader


def df_to_records(df: pd.DataFrame) -> list:
    """Serialize a DataFrame to JSON-safe records.

    pandas.to_json handles Timestamps and other non-standard types that
    the default json encoder cannot, so we round-trip through it.
    """
    return json.loads(df.to_json(orient="records", date_format="iso", default_handler=str))

app = FastAPI(title="Dashboard API", version="1.0.0")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

loader = get_loader()


class FilterConfig(BaseModel):
    """Filter configuration model"""
    column: str
    operator: str  # 'eq', 'contains', 'gt', 'lt', 'gte', 'lte', 'in'
    value: Any


class SliceRequest(BaseModel):
    """Request model for data slicing"""
    file: str
    filters: List[FilterConfig] = []
    columns: Optional[List[str]] = None
    sort_by: Optional[str] = None
    sort_order: str = "asc"
    limit: Optional[int] = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/files")
async def list_files():
    """Get list of all available data files"""
    try:
        files = loader.get_excel_files()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/file-info")
async def get_file_info():
    """Get detailed information about all files"""
    try:
        info = loader.get_file_info()
        return {"files": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/file/{filename}")
async def get_file_data(filename: str):
    """Get full data from a file"""
    try:
        df = loader.load_file(filename)
        return {
            "filename": filename,
            "rows": len(df),
            "columns": df.columns.tolist(),
            "data": df_to_records(df.head(1000))
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/slice")
async def slice_data(request: SliceRequest):
    """Slice and filter data dynamically"""
    try:
        df = loader.load_file(request.file)
        
        # Apply filters
        for filter_config in request.filters:
            df = apply_filter(df, filter_config)
        
        # Select columns
        if request.columns:
            available_cols = [c for c in request.columns if c in df.columns]
            df = df[available_cols]
        
        # Sort
        if request.sort_by and request.sort_by in df.columns:
            ascending = request.sort_order.lower() == "asc"
            df = df.sort_values(by=request.sort_by, ascending=ascending)
        
        # Limit results
        if request.limit:
            df = df.head(request.limit)
        
        return {
            "filename": request.file,
            "rows": len(df),
            "columns": df.columns.tolist(),
            "data": df_to_records(df)
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/file/{filename}/summary")
async def get_file_summary(filename: str):
    """Get statistical summary of a file"""
    try:
        df = loader.load_file(filename)
        
        summary = {
            "filename": filename,
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "columns": []
        }
        
        for col in df.columns:
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isna().sum()),
                "unique_count": int(df[col].nunique())
            }
            
            # Add numeric stats if applicable
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info.update({
                    "min": float(df[col].min()) if not df[col].isna().all() else None,
                    "max": float(df[col].max()) if not df[col].isna().all() else None,
                    "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                    "median": float(df[col].median()) if not df[col].isna().all() else None,
                })
            
            summary["columns"].append(col_info)
        
        return summary
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/file/{filename}/unique-values")
async def get_unique_values(
    filename: str,
    column: str = Query(..., description="Column name"),
    limit: int = Query(100, description="Maximum number of unique values")
):
    """Get unique values for a column (for filter dropdowns)"""
    try:
        df = loader.load_file(filename)
        
        if column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{column}' not found")
        
        unique_vals = df[column].dropna().unique()[:limit]
        return {
            "column": column,
            "unique_values": [str(v) for v in unique_vals],
            "count": len(unique_vals)
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def apply_filter(df: pd.DataFrame, filter_config: FilterConfig) -> pd.DataFrame:
    """Apply a single filter to the dataframe"""
    col = filter_config.column
    op = filter_config.operator
    val = filter_config.value
    
    if col not in df.columns:
        return df
    
    if op == 'eq':
        return df[df[col] == val]
    elif op == 'contains':
        return df[df[col].astype(str).str.contains(str(val), case=False, na=False)]
    elif op == 'gt':
        return df[df[col] > val]
    elif op == 'lt':
        return df[df[col] < val]
    elif op == 'gte':
        return df[df[col] >= val]
    elif op == 'lte':
        return df[df[col] <= val]
    elif op == 'in':
        return df[df[col].isin(val if isinstance(val, list) else [val])]
    else:
        return df


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
