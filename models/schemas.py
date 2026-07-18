"""
Pydantic data models — mirrors vite-deneme-bonus/src/lib/types.ts exactly.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    """Mongo / frontend dokümanları ekstra alan taşıyabilir."""

    model_config = ConfigDict(extra="ignore")


# ─── colours & icons ────────────────────────────────────────────────────────

class ColorShade(ApiModel):
    main: Optional[str] = None
    dark: Optional[str] = None
    light: Optional[str] = None


class BgShade(ApiModel):
    main: Optional[str] = None
    card: Optional[str] = None
    alt: Optional[str] = None


class TextShade(ApiModel):
    main: Optional[str] = None
    secondary: Optional[str] = None
    muted: Optional[str] = None


class SiteColors(ApiModel):
    primary: Optional[ColorShade] = None
    background: Optional[BgShade] = None
    text: Optional[TextShade] = None


# ─── board (card) ────────────────────────────────────────────────────────────

class Board(ApiModel):
    id: int
    baslik: Optional[str] = None
    altbaslik: Optional[str] = None
    siteadi: Optional[str] = None
    url: Optional[str] = None
    resimurl: Optional[str] = None
    gifurl: Optional[str] = None
    slider: Optional[str] = None
    sira: Optional[int] = None
    catid: Optional[int] = None
    site_id: Optional[int] = None
    pinnedTable: Optional[int] = None
    pinnedSTable: Optional[int] = None
    groupp: Optional[int] = None
    durum: Optional[int] = None
    durums: Optional[int] = None
    popuporder: Optional[int] = None
    storyimage: Optional[str] = None
    storytext: Optional[str] = None
    image: Optional[str] = None
    storytext2: Optional[str] = None
    sticky: Optional[bool] = None
    verificationimage: Optional[str] = None
    WinnersID: Optional[int] = None
    WheelID: Optional[int] = None


class BoardCreate(ApiModel):
    """Fields allowed when creating/updating a board (id auto-assigned)."""

    baslik: Optional[str] = None
    altbaslik: Optional[str] = None
    siteadi: Optional[str] = None
    url: Optional[str] = None
    resimurl: Optional[str] = None
    gifurl: Optional[str] = None
    slider: Optional[str] = "0"
    sira: Optional[int] = 0
    catid: Optional[int] = None
    site_id: Optional[int] = None
    pinnedTable: Optional[int] = 0
    pinnedSTable: Optional[int] = 0
    groupp: Optional[int] = 0
    durum: Optional[int] = None
    durums: Optional[int] = 1
    popuporder: Optional[int] = 0
    storyimage: Optional[str] = None
    storytext: Optional[str] = None
    image: Optional[str] = None
    storytext2: Optional[str] = None
    sticky: Optional[bool] = False
    verificationimage: Optional[str] = None
    WinnersID: Optional[int] = None
    WheelID: Optional[int] = None


# ─── category ────────────────────────────────────────────────────────────────

class Category(ApiModel):
    id: int
    title: Optional[str] = None
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    order: Optional[int] = 0
    boards: list[Board] = Field(default_factory=list)


class CategoryCreate(ApiModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    order: Optional[int] = 0


# ─── text items (header / footer links) ──────────────────────────────────────

class TextItem(ApiModel):
    id: int
    baslik: Optional[str] = None
    url: Optional[str] = None
    tip: Optional[str] = None
    durum: Optional[int] = 1


class TextItemCreate(ApiModel):
    baslik: Optional[str] = None
    url: Optional[str] = None
    tip: Optional[str] = "header"
    durum: Optional[int] = 1


# ─── popup items ─────────────────────────────────────────────────────────────

class PopupItem(ApiModel):
    id: int
    resimurl: Optional[str] = None
    url: Optional[str] = None
    popuporder: Optional[int] = 0
    durum: Optional[int] = 1
    baslik: Optional[str] = None
    altbaslik: Optional[str] = None
    button_text: Optional[str] = None
    buttonText: Optional[str] = None


class PopupItemCreate(ApiModel):
    resimurl: Optional[str] = None
    url: Optional[str] = None
    popuporder: Optional[int] = 0
    durum: Optional[int] = 1
    baslik: Optional[str] = None
    altbaslik: Optional[str] = None
    button_text: Optional[str] = None
    buttonText: Optional[str] = None


# ─── games (stories / groups) ────────────────────────────────────────────────

class GamesStory(ApiModel):
    name: Optional[str] = None
    image: Optional[str] = None
    storyimage: Optional[str] = None
    storytext: Optional[str] = None
    sticky: Optional[bool] = False


class GamesGroup(ApiModel):
    category_id: Optional[int] = None
    order: Optional[int] = 0
    verificationimage: Optional[str] = None
    games: list[GamesStory] = Field(default_factory=list)


# ─── banner item ─────────────────────────────────────────────────────────────

class BannerItem(ApiModel):
    id: Optional[int] = None
    image: Optional[str] = None
    href: Optional[str] = None
    title: Optional[str] = None
    order: Optional[int] = 0


class BannerItemCreate(ApiModel):
    image: Optional[str] = None
    href: Optional[str] = None
    title: Optional[str] = None
    order: Optional[int] = 0


# ─── site (root config) ──────────────────────────────────────────────────────

class SiteConfig(ApiModel):
    id: int
    baslik: Optional[str] = None
    description: Optional[str] = None
    renk: Optional[str] = None
    favicon: Optional[str] = None
    menu1: Optional[str] = None
    menu2: Optional[str] = None
    menu3: Optional[str] = None
    menu4: Optional[str] = None
    mteams: Optional[str] = None
    sekil: Optional[str] = None
    noticatid: Optional[int] = None
    tablosplash: Optional[int] = None
    searchPlaceholder: Optional[str] = None
    gamesStripTitle: Optional[str] = None
    homeExtraTitle: Optional[str] = None
    homeExtraBody: Optional[str] = None
    homeExtraLinks: Optional[list[Any]] = None
    premiumCount: Optional[int] = None
    pinnedPopup: Optional[int] = None
    pinned1: Optional[int] = None
    pinned2: Optional[int] = None
    pinned3: Optional[int] = None
    pinned4: Optional[int] = None
    pinned5: Optional[int] = None
    pinned6: Optional[int] = None
    siteColors: Optional[SiteColors] = None
    colors: Optional[Any] = None
    icons: Optional[dict[str, str]] = None
    siteIcons: Optional[dict[str, str]] = None
    banners: list[BannerItem] = Field(default_factory=list)
    sweepstakes: Optional[Any] = None
    games: Optional[Any] = None
    WinnersID: Optional[int] = None
    WheelID: Optional[int] = None


class SiteConfigUpdate(ApiModel):
    """Partial update – all fields optional."""

    baslik: Optional[str] = None
    description: Optional[str] = None
    renk: Optional[str] = None
    favicon: Optional[str] = None
    menu1: Optional[str] = None
    menu2: Optional[str] = None
    menu3: Optional[str] = None
    menu4: Optional[str] = None
    mteams: Optional[str] = None
    searchPlaceholder: Optional[str] = None
    premiumCount: Optional[int] = None
    pinnedPopup: Optional[int] = None
    pinned1: Optional[int] = None
    pinned2: Optional[int] = None
    pinned3: Optional[int] = None
    pinned4: Optional[int] = None
    pinned5: Optional[int] = None
    pinned6: Optional[int] = None
    siteColors: Optional[SiteColors] = None
    siteIcons: Optional[dict[str, str]] = None
    sweepstakes: Optional[Any] = None
    games: Optional[Any] = None
    WinnersID: Optional[int] = None
    WheelID: Optional[int] = None


# ─── full API response shape (mirrors BonusData in types.ts) ─────────────────

class BonusDataResponse(ApiModel):
    categories: list[Category] = Field(default_factory=list)
    texts: dict[str, list[TextItem]] = Field(default_factory=dict)
    popups: dict[str, list[PopupItem]] = Field(default_factory=dict)
    big: list[Board] = Field(default_factory=list)
    site: SiteConfig
