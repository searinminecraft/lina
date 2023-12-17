import globals
import aiohttp

import xml.etree.ElementTree as et


async def updateDb():
    async with aiohttp.ClientSession(
            "https://online.supertuxkart.net"
            ) as session:
        async with session.get("/downloads/xml/online_assets.xml") as r:
            data = et.fromstring(await r.text())

    addons = []
    addonsdict = {}
    for a in data.findall("track"):
        addons.append((
            a.attrib["id"],
            a.attrib["name"],
            a.attrib["file"],
            int(a.attrib["date"]),
            a.attrib["uploader"],
            a.attrib["designer"],
            a.attrib["description"],
            a.get("image", ""),
            int(a.attrib["format"]),
            int(a.attrib["revision"]),
            int(a.attrib["status"]),
            int(a.attrib["size"]),
            float(a.attrib["rating"])
        ))

        addonsdict[a.attrib["id"]] = {
            "id": a.attrib["id"],
            "name":  a.attrib["name"],
            "file": a.attrib["file"],
            "date": int(a.attrib["date"]),
            "uploader": a.attrib["uploader"],
            "designer": a.attrib["designer"],
            "description": a.attrib["description"],
            "image": a.get("image", ""),
            "format": int(a.attrib["format"]),
            "revision": int(a.attrib["revision"]),
            "status": int(a.attrib["status"]),
            "size": int(a.attrib["size"]),
            "rating": float(a.attrib["rating"])
        }

    prepearedSmt = await globals.pgconn.prepare("""INSERT INTO addons
    (id, name, file, date, uploader, designer, description,
    image, format, revision, status, size, rating)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
    ON CONFLICT (id) DO UPDATE SET
    id = $1,
    name = $2,
    file = $3,
    date = $4,
    uploader = $5,
    designer = $6,
    description = $7,
    image = $8,
    format = $9,
    revision = $10,
    status = $11,
    size = $12,
    rating = $13;""")

    await prepearedSmt.executemany(addons)

    globals.addons = addonsdict
