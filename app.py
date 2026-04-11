from functools import lru_cache
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Nissan Automotive Benchmark API")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    df = pd.read_csv("nissan_dataset.csv")
    df["year"] = df["year"].astype(int)
    df["ex_showroom_price"] = df["ex_showroom_price"].astype(float)
    df["quoted_price"] = df["quoted_price"].astype(float)
    return df


def filter_data(
    market: Optional[str] = None,
    model: Optional[str] = None,
    year: Optional[int] = None,
) -> pd.DataFrame:
    df = load_data()
    filtered = df.copy()
    if market and market != "All":
        filtered = filtered[filtered["market"] == market]
    if model and model != "All":
        filtered = filtered[filtered["model"] == model]
    if year is not None:
        filtered = filtered[filtered["year"] == year]
    return filtered


def build_filters(df: pd.DataFrame) -> Dict[str, List[Any]]:
    return {
        "markets": ["All"] + sorted(df["market"].dropna().unique().tolist()),
        "models": ["All"] + sorted(df["model"].dropna().unique().tolist()),
        "years": ["All"] + sorted(df["year"].dropna().astype(int).unique().tolist()),
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/filters")
def get_filters() -> JSONResponse:
    df = load_data()
    return JSONResponse(build_filters(df))


@app.get("/api/dashboard")
def get_dashboard(
    market: str = Query("All"),
    model: str = Query("All"),
    year: Optional[int] = Query(None),
) -> JSONResponse:
    filtered = filter_data(market=market, model=model, year=year)

    kpis = {
        "unique_models": int(filtered["model"].nunique()),
        "unique_trims": int(filtered["trim"].nunique()),
        "avg_ex_showroom_price": float(filtered["ex_showroom_price"].mean()) if not filtered.empty else 0.0,
        "avg_discount": float(filtered["discount_offer"].mean()) if not filtered.empty else 0.0,
    }

    price_trend = []
    if not filtered.empty:
        grouped = (
            filtered.groupby(["model", "year"])["ex_showroom_price"]
            .mean()
            .reset_index()
        )
        for model_name, model_df in grouped.groupby("model"):
            price_trend.append(
                {
                    "name": model_name,
                    "years": model_df["year"].tolist(),
                    "prices": model_df["ex_showroom_price"].round(2).tolist(),
                }
            )

    feature_data = []
    if not filtered.empty:
        feature_df = (
            filtered.groupby("model")[
                ["infotainment_size_inch", "ADAS_level", "airbags", "safety_rating"]
            ]
            .mean(numeric_only=True)
            .round(2)
            .reset_index()
        )
        feature_data = feature_df.to_dict(orient="records")

    positioning = []
    if not filtered.empty:
        positioning_df = (
            filtered.groupby("model")["positioning_score"]
            .mean(numeric_only=True)
            .round(2)
            .reset_index()
            .sort_values(by="positioning_score", ascending=False)
        )
        positioning = positioning_df.to_dict(orient="records")

    quote_data = []
    if not filtered.empty:
        quote_df = (
            filtered.groupby("model")["quoted_price"]
            .mean(numeric_only=True)
            .round(2)
            .reset_index()
            .sort_values(by="quoted_price", ascending=False)
        )
        quote_data = quote_df.to_dict(orient="records")

    comparison = []
    if not filtered.empty:
        comparison_df = (
            filtered.groupby("model")[
                ["ex_showroom_price", "quoted_price", "discount_offer", "positioning_score"]
            ]
            .mean(numeric_only=True)
            .round(2)
            .reset_index()
            .sort_values(by="ex_showroom_price")
        )
        comparison = comparison_df.to_dict(orient="records")

    return JSONResponse(
        {
            "filters": {"market": market, "model": model, "year": year},
            "kpis": kpis,
            "price_trend": price_trend,
            "feature_data": feature_data,
            "positioning": positioning,
            "quote_data": quote_data,
            "comparison": comparison,
            "row_count": len(filtered),
        }
    )


@app.get("/api/data")
def get_data(
    market: str = Query("All"),
    model: str = Query("All"),
    year: Optional[int] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
) -> JSONResponse:
    filtered = filter_data(market=market, model=model, year=year)
    rows = filtered.head(limit).to_dict(orient="records")
    return JSONResponse({"count": len(filtered), "limit": limit, "rows": rows})
