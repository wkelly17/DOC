<script lang="ts">
  import LoadingIndicator from './LoadingIndicator.svelte'
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'
  import { otBookStore, ntBookStore } from '../stores/BooksStore'

  // Get the lang codes from the store reactively.
  $: lang0Code = $lang0NameAndCode.toString().split(',')[1]?.split(': ')[1]
  $: lang1Code = $lang1NameAndCode.toString().split(',')[1]?.split(': ')[1]
  // Get the lang names from the store reactively.
  // $: lang0Name = $lang0NameAndCode.toString().split(',')[0]
  // $: lang1Name = $lang1NameAndCode.toString().split(',')[0]

  export async function getResourceTypes(
    langCode: string,
    resourceCodeAndNames: Array<string>,
    apiRootUrl = <string>import.meta.env.VITE_BACKEND_API_URL,
    sharedResourceTypesUrl = <string>import.meta.env.VITE_SHARED_RESOURCE_TYPES_URL
  ): Promise<Array<Array<string>>> {
    const url_ = `${apiRootUrl}${sharedResourceTypesUrl}${langCode}/`
    const url = new URL(url_)
    resourceCodeAndNames.map(resourceCodeAndName =>
      url.searchParams.append('resource_codes', resourceCodeAndName[0])
    )
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const json = await response.json()
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    const codes = json.map((x: string[]) => x[0])
    console.log(`codes: ${codes}`)
    return json
  }
</script>

<h3>{$lang0NameAndCode[1]}'s resource types</h3>
<div>
  {#await getResourceTypes(lang0Code, [...$otBookStore, ...$ntBookStore])}
    <LoadingIndicator />
  {:then data}
    <span>{data}</span>
  {:catch error}
    <p class="error">{error.message}</p>
  {/await}
</div>

<h3>{$lang1NameAndCode[1]}'s resource types</h3>
<div>
  {#await getResourceTypes(lang1Code, [...$otBookStore, ...$ntBookStore])}
    <LoadingIndicator />
  {:then data}
    <span>{data}</span>
  {:catch error}
    <p class="error">{error.message}</p>
  {/await}
</div>
