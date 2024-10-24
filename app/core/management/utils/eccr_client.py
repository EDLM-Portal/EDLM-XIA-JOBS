import logging

import requests

from core.models import ECCRConfiguration

logger = logging.getLogger('dict_config_logger')


def get_eccr_api_endpoint():
    """Setting API endpoint from ECCR communication """
    logger.debug("Retrieve xsr_api_endpoint from XSR configuration")

    eccr_obj = ECCRConfiguration.objects.first()

    if not eccr_obj:
        logger.error("ECCR API endpoint not set, please set endpoint")
        return None
    eccr_endpoint = eccr_obj.eccr_api_endpoint
    return eccr_endpoint


def get_eccr_UUID(code):
    """Setting ECCR UUID using CWR Code communication """

    if not get_eccr_api_endpoint():
        logger.error("ECCR API endpoint not set, please set endpoint")
        return None

    url = get_eccr_api_endpoint() + "/api/sky/repo/search"

    cwr_code = '(markings:' + code + ')'

    payload = {'data': cwr_code,
               'searchParams': '{"start":0,"size":20}'}

    files = [

    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload,
                                files=files)

    job_resp = {'job': {
                        'reference': "",
                        'job_type': "",
                        'name': ""
                    }
                }

    if not response.json():
        return None
    elif response.json()[0]['@id']:

        job_resp['job']['reference'] = response.json()[0]['@id']

        if response.json()[0]['@type']:

            job_resp['job']['job_type'] = response.json()[0]['@type']

        if response.json()[0]['name']['@value']:

            job_resp['job']['name'] = response.json()[0]['name']['@value']

        return job_resp
    else:
        return None
