# Interleaved Resource Generator API otherwise known as DOC

A DocumentRequest, composed of ResourceRequests, and an assembly
strategy, is submitted to the API. The API then uses that information
to fetch assets associated with each Resource and interleaves said
assets according to the assembly strategy chosen. It also builds
interlinking between assets within the document as appropriate and
then translates the assets into an HTML document. Finally the API
generates a PDF from the HTML document.

Each Resource is composed of lang_code, resource_type, and
resource_code.

There are over 500 lang_codes, several different resource_types, and
at least 66 resource_codes.

There are a few different assembly strategies available.

In this way, the API can produce multi-language, multi-book,
multi-resource PDFs assembled according to the resources and assembly
strategy combinations chosen.
