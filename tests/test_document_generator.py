from typing import List

import logging
import yaml


from document import config
from document.domain import model
from document.domain import document_generator


with open(config.get_logging_config_file_path(), "r") as f:
    logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)


def main() -> None:
    # payload = {}
    # payload["resources"] = [
    #     # {"lang_code": "am", "resource_type": "ulb", "resource_code": ""},
    #     # {"lang_code": "erk-x-erakor", "resource_type": "reg", "resource_code": "eph"},
    #     # {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "eph"},
    #     # {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "lev"},
    #     # {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "lev"},
    #     # FIXME ml, tn, tit doesn't exist, but tn for all books does
    #     # {"lang_code": "ml", "resource_type": "tn", "resource_code": "tit"},
    #     # Next two:
    #     # {"lang_code": "en", "resource_type": "ulb-wa", "resource_code": "gen"},
    #     # {"lang_code": "en", "resource_type": "tn-wa", "resource_code": "gen"},
    #     {"lang_code": "ml", "resource_type": "ulb", "resource_code": "tit"},
    #     # {"lang_code": "as", "resource_type": "tn", "resource_code": "rev"},
    #     # # {"lang_code": "ml", "resource_type": "obs-tq", "resource_code": ""},
    #     # {"lang_code": "mr", "resource_type": "udb", "resource_code": "mrk"},
    # ]
    # payload["assembly_strategy"] = "book"  # verse, chapter, book

    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.BOOK
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", resource_code="gen"
        )
    )
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tn-wa", resource_code="gen"
        )
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()


if __name__ == "__main__":
    main()
