import yaml
from pathlib import Path
from zotero2qmd.pub_type_translate import zotero_to_csl

def filter_pubs(pub_list: list)->list:
    valid_items =  [x for x in pub_list if "data" in x]
    return [x for x in valid_items if x["data"]["itemType"] in zotero_to_csl]

def make_authors(item: dict) -> dict:
    try:
        creators = item["creators"]
    except:
        ValueError
    
    creator_type = set([x["creatorType"] for x in creators])

    return {
        cre:
        [
            {"name":
                {
                    "given": x["firstName"],
                    "family": x["lastName"]
                }
            }
            for x in creators if x["creatorType"] == cre
        ]
            for cre in creator_type
        }

def unique_path(directory, stem):
    name_pattern = "{stem}_{counter:02d}.qmd"
    counter = 0
    while True:
        counter += 1
        path = directory / name_pattern.format(stem = stem, counter = counter)
        if not path.exists():
            return path

def make_file_path(base_path, main_dict):
    stem = main_dict["author"][0]["name"]["family"] + \
            main_dict["date"].split("-")[0]
    
    return base_path.joinpath(stem).with_suffix(".qmd")
    


def get_container(item):
    if "versionNumber" in item:
        return item["versionNumber"]
    if "publicationTitle" in item:
        return item["publicationTitle"]
    if "proceedingsTitle" in item:
        return item["proceedingsTitle"]
    if "bookTitle" in item:
        return item["bookTitle"]

    return ''

def item2main(
        pub_item: dict
        ):
    try:
        pub_data = pub_item["data"]
    except:
        raise ValueError
    main_dict = {}
    citation_dict = {}

    citation_dict["type"] = zotero_to_csl[pub_data["itemType"]]
    
    if "volume" in pub_data:
        citation_dict["volume"] = pub_data["volume"]
    
    if "number" in pub_data:
        citation_dict["number"] = pub_data["number"]
    
    if "issue" in pub_data:
        citation_dict["issue"] = pub_data["issue"]

    if "pages" in pub_data and len(pub_data["pages"])>0:
        citation_dict["page"] = pub_data["pages"]
    
    if "extra" in pub_data:
        main_dict["params"] = {"notes" : pub_data["extra"]}


    authors = make_authors(pub_data)

    if "author" in authors:
        main_dict["author"] = authors["author"]
    if "programmer" in authors:
        main_dict["author"] = authors["programmer"]

    for k in authors:
        if not k == "author" and not k == "programmer":
            citation_dict[k] = authors[k]

    main_dict["title"] = pub_data["title"]
    main_dict["date"] = pub_data["date"]
    main_dict["date-format"] = "YYYY"
    citation_dict["issued"] = pub_data["date"]

    if "DOI" in pub_data:
        main_dict["doi"] = pub_data["DOI"]
    if "url" in pub_data:
        citation_dict["url"] = pub_data["url"]
    
    if "versionNumber" not in pub_data:
        citation_dict["container-title"] = get_container(pub_data)
        
    main_dict["description"] = get_container(pub_data)

    if "abstractNote" in pub_data:
        main_dict["abstract"] = pub_data["abstractNote"]

    main_dict["citation"] = citation_dict
    return main_dict

def main2qmd(out_path, main_dict):
    qmd_path = make_file_path(out_path, main_dict)
    main_yaml = yaml.dump(main_dict)
    qmd_yaml = "---\n" + main_yaml + "\n---"

    with qmd_path.open(mode = 'w') as out_qmd:
        out_qmd.write(qmd_yaml)


