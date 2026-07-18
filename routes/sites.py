"""
Public bonus-panel endpoints:
  GET /api/site-data
  GET /api/data.php   (JS loader)
"""
from __future__ import annotations

import glob as _glob
import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse

import storage
from models.schemas import BonusDataResponse

router = APIRouter(tags=["sites"])

BASE_DIR = Path(__file__).resolve().parent.parent
_env_assets = os.environ.get("VITE_ASSETS_DIR")
VITE_ASSETS = (
    Path(_env_assets)
    if _env_assets
    else BASE_DIR.parent / "Yazilimlarim" / "vite-deneme-bonus" / "dist" / "assets"
)
# Fallback: Desktop sibling path used in local layout
if not VITE_ASSETS.exists():
    alt = BASE_DIR.parent / "vite-deneme-bonus" / "dist" / "assets"
    if alt.exists():
        VITE_ASSETS = alt


def _pick_latest(pattern: str) -> str | None:
    files = _glob.glob(pattern)
    return max(files, key=os.path.getmtime) if files else None


def _get_entry_assets() -> tuple[str | None, str | None]:
    css = _pick_latest(str(VITE_ASSETS / "index-*.css"))
    js = _pick_latest(str(VITE_ASSETS / "index-*.js"))
    return (
        Path(css).name if css else None,
        Path(js).name if js else None,
    )


def _js_str(value: str) -> str:
    return json.dumps(value)


@router.get("/site-data", response_model=BonusDataResponse)
def api_site_data(site_id: int = 3, _: str | None = None) -> JSONResponse:
    """Returns the full site data as JSON for Vite apps / workers."""
    site_doc = storage.load_site(site_id)
    if site_doc is None:
        raise HTTPException(404, f"Site {site_id} not found")

    big: list[dict] = []
    for cat in site_doc.get("categories", []):
        for board in cat.get("boards", []):
            if str(board.get("slider", "")) == "2":
                big.append(board)

    payload = {**site_doc, "big": big}
    return JSONResponse(BonusDataResponse.model_validate(payload).model_dump(mode="json"))


@router.get("/data.php", response_class=PlainTextResponse)
def api_loader(
    request: Request,
    site_id: int = 3,
    _: str | None = None,
) -> PlainTextResponse:
    """
    Self-executing JS snippet:
      1. window.__BONUS_DATA__
      2. window.SITE_CONFIG
      3. Vite CSS + JS injection
    """
    if not VITE_ASSETS.exists():
        return PlainTextResponse(
            "console.error('Vite dist not found – set VITE_ASSETS_DIR or build vite-deneme-bonus');",
            media_type="application/javascript",
        )

    css_name, js_name = _get_entry_assets()
    if not js_name:
        return PlainTextResponse(
            "console.error('No Vite entry JS found in dist/assets');",
            media_type="application/javascript",
        )

    base = str(request.base_url).rstrip("/")
    js_url = f"{base}/assets/{js_name}"
    css_inject = ""
    if css_name:
        css_url = f"{base}/assets/{css_name}"
        css_inject = (
            f"var l=document.createElement('link');"
            f"l.rel='stylesheet';"
            f"l.href={_js_str(css_url)};"
            f"document.head.appendChild(l);"
        )

    site_data = storage.load_site(site_id)
    raw_json = "null" if site_data is None else json.dumps(site_data, ensure_ascii=False)

    loader = f"""(function(){{
  try{{
    window.SITE_CONFIG={{"site_id":{int(site_id)}}};
    window.__BONUS_DATA__={raw_json};
    if("serviceWorker" in navigator){{
      navigator.serviceWorker.getRegistrations().then(function(r){{
        for(var i=0;i<r.length;i++)r[i].unregister();
      }});
    }}
    if("caches" in window){{
      caches.keys().then(function(k){{
        for(var i=0;i<k.length;i++)caches.delete(k[i]);
      }});
    }}
  }}catch(e){{}}
  function ensureRoot(){{
    var el=document.getElementById('root');
    if(!el){{el=document.createElement('div');el.id='root';document.body.appendChild(el);}}
  }}
  ensureRoot();
  {css_inject}
  var s=document.createElement('script');
  s.type='module';
  s.crossOrigin='anonymous';
  s.src={_js_str(js_url)};
  document.body.appendChild(s);
}})();"""

    return PlainTextResponse(loader, media_type="application/javascript")
