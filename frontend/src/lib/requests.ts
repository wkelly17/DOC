const langCodeRegex = /.*\(language code: (.*?)\)/

/**
 * Extract the language code from the menu option selected.
 * Presupposes that menu options are in the following format:
 * 'English (language code: en)'
 **/
export function extractLanguageCode(languageString: string): string {
  let matchStrings = languageString.match(langCodeRegex)
  if (matchStrings) {
    return matchStrings[1]
  } else {
    throw new Error('Invalid menu selection chosen') // This won't happen, but make tsc happy
  }
}

let API_ROOT_URL: string = <string>import.meta.env.VITE_BACKEND_API_URL

const RESOURCE_CODES_FOR_LANG: string = '/resource_codes_for_lang/'
const SHARED_RESOURCE_CODES: string = '/shared_resource_codes/'

export async function getLang0ResourceCodes(langCode: string): Promise<string[]> {
  const response = await fetch(API_ROOT_URL + RESOURCE_CODES_FOR_LANG + langCode)
  const json = await response.json()
  if (response.ok) {
    return <string[]>json
  } else {
    throw new Error(json)
  }
}

export async function getSharedResourceCodes(
  lang0Code: string,
  lang1Code: string
): Promise<string[]> {
  const response = await fetch(
    API_ROOT_URL + SHARED_RESOURCE_CODES + lang0Code + '/' + lang1Code
  )
  const json = await response.json()
  if (response.ok) {
    return <string[]>json
  } else {
    throw new Error(json)
  }
}
