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

const API_ROOT_URL = <string>import.meta.env.VITE_BACKEND_API_URL
const RESOURCE_CODES_FOR_LANG = <string>import.meta.env.RESOURCE_CODES_FOR_LANG
const SHARED_RESOURCE_CODES = <string>import.meta.env.SHARED_RESOURCE_CODES

export async function getLang0ResourceCodes(langCode: string): Promise<string[]> {
  const response = await fetch(API_ROOT_URL + RESOURCE_CODES_FOR_LANG + langCode)
  const json = await response.json()
  if (!response.ok) throw new Error(json)
  return <string[]>json
}

// export async function getSharedResourceCodes(
//   lang0Code: string,
//   lang1Code: string
// ): Promise<string[]> {
//   const response = await fetch(
//     API_ROOT_URL + SHARED_RESOURCE_CODES + lang0Code + '/' + lang1Code
//   )
//   const json = await response.json()
//   if (!response.ok) throw new Error(response.statusText)
//   return <string[]>json
// }

// Alternative based on https://github.com/whatwg/fetch/issues/18#issuecomment-605629519
// export async function getSharedResourceCodes(
//   lang0Code: string,
//   lang1Code: string
// ): Promise<string[]> {
//   return = await fetch(
//     API_ROOT_URL + SHARED_RESOURCE_CODES + lang0Code + '/' + lang1Code
//   ).then((response) =>
//     response.json().then((data) => {
//       if (!response.ok) {
//         throw Error(data.err || 'HTTP error')
//       }
//       return <string[]>data
//     }))
// }
