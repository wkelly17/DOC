<script lang="ts">
  // This page exists to service the use case where BIEL wants to hand off
  // to DOC by providing only a repo URL and have DOC populate state
  // as if the user had started on DOC. Here is an example URL that
  // would work:
  // http(s)://<DOC base url here>/transfer/repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fbahasatech.indotengah%2Fbne_gal_text_reg&book_name=Galatians
  // or
  // http(s)://<DOC base url here>/transfer/repo_url=https:%2F%2Fcontent.bibletranslationtools.org%2FWycliffeAssociates%2Fen_ulb

  import type { PageData } from './$types'
  import {
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore,
    langCodesStore,
    langNamesStore,
    langCountStore
  } from '$lib/stores/LanguagesStore'
  import { ntBookStore, otBookStore, bookCountStore } from '$lib/stores/BooksStore'
  import { resourceTypesStore, resourceTypesCountStore } from '$lib/stores/ResourceTypesStore'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import otBooks from '$lib/ot-books'
  import ntBooks from '$lib/nt-books'
  import { booksMap } from '$lib/bible-books'
  import { routeToPage } from '$lib/utils'
  import {
    PUBLIC_LANG_CODES_NAMES_URL,
    PUBLIC_SHARED_RESOURCE_TYPES_URL,
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import { getCode, getName } from '$lib/utils'

  export let data: PageData

  async function getLangCodesNames(
    apiRootUrl: string = env.PUBLIC_BACKEND_API_URL,
    langCodesAndNamesUrl: string = <string>PUBLIC_LANG_CODES_NAMES_URL
  ): Promise<Array<[string, string, boolean]>> {
    const response = await fetch(`${apiRootUrl}${langCodesAndNamesUrl}`)
    const langCodeNameAndTypes: Array<[string, string, boolean]> = await response.json()
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    return langCodeNameAndTypes
  }

  async function getResourceTypesAndNames(
    langCode: string,
    bookCodeAndNames: Array<[string, string]>,
    apiRootUrl = <string>env.PUBLIC_BACKEND_API_URL,
    sharedResourceTypesUrl = <string>PUBLIC_SHARED_RESOURCE_TYPES_URL
  ): Promise<Array<[string, string, string]>> {
    // Form the URL to ultimately invoke
    // resource_lookup.shared_resource_types.
    const url_ = `${apiRootUrl}${sharedResourceTypesUrl}${langCode}/`
    const url = new URL(url_)
    bookCodeAndNames.map((bookCodeAndName) =>
      url.searchParams.append('book_codes', bookCodeAndName[0])
    )
    const response = await fetch(url)
    const resourceTypesAndNames: Array<[string, string]> = await response.json()
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }

    // Associate the langCode to each resource type code and name pair
    return resourceTypesAndNames.map((element) => [langCode, element[0], element[1]])
  }

  let langCodeNameAndTypes: Array<[string, string, boolean]> = []
  let filteredLangCodeNameAndTypes: Array<[string, string, boolean]> = []
  let filteredResourceTypesAndNames: Array<[string, string, string]> = []
  let message: string = ''
  let errorMessage: string = ''

  const components = data.repo?.split('_') || []
  let langCode: string
  let bookCode: string
  let nada: string
  let resource: string
  if (components.length === 4) {
    // e.g., repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fbahasatech.indotengah%2Fbne_gal_text_reg&book_name=Galatians
    langCode = components[0]
    bookCode = components[1]
    nada = components[2]
    resource = components[3]
    console.log(
      `Transferred values from BIEL, langCode: ${langCode}, bookCode: ${bookCode}, resource: ${resource}`
    )
    message = `You've requested the following values, langCode: ${langCode}, bookCode: ${bookCode}, resource: ${resource}`
    getLangCodesNames()
      .then((langCodeNameAndTypes_) => {
        langCodeNameAndTypes = langCodeNameAndTypes_

        filteredLangCodeNameAndTypes = langCodeNameAndTypes_.filter(
          (element: [string, string, boolean]) => {
            return element[0] === langCode
          }
        )
        console.log(`filteredLangCodeNameAndTypes: ${filteredLangCodeNameAndTypes}`)
        if (filteredLangCodeNameAndTypes.length > 0) {
          $langCodesStore.push(filteredLangCodeNameAndTypes[0][0])
          $langNamesStore.push(filteredLangCodeNameAndTypes[0][1])
          if (filteredLangCodeNameAndTypes[0][2]) {
            $gatewayCodeAndNamesStore.push(
              `${filteredLangCodeNameAndTypes[0][0]}, ${filteredLangCodeNameAndTypes[0][1]}`
            )
          } else {
            $heartCodeAndNamesStore.push(
              `${filteredLangCodeNameAndTypes[0][0]}, ${filteredLangCodeNameAndTypes[0][1]}`
            )
          }
          $langCountStore = 1
          // console.log(`$langCodesStore: ${$langCodesStore}`)
          // console.log(`$gatewayCodeAndNamesStore: ${$gatewayCodeAndNamesStore}`)
          // console.log(`$heartCodeAndNamesStore: ${$heartCodeAndNamesStore}`)

          if (otBooks.includes(bookCode)) {
            $otBookStore.push(`${bookCode}, ${booksMap[bookCode]}`)
            // console.log(`$otBookStore: ${otBookStore}`)
            $bookCountStore = 1
          } else {
            $ntBookStore.push(`${bookCode}, ${booksMap[bookCode]}`)
            // console.log(`$ntBookStore: ${$ntBookStore}`)
            $bookCountStore = 1
          }
          let otResourceCodes_: Array<[string, string]> = $otBookStore.map((item) => [
            getCode(item),
            getName(item)
          ])
          let ntResourceCodes_: Array<[string, string]> = $ntBookStore.map((item) => [
            getCode(item),
            getName(item)
          ])
          if ($langCodesStore[0]) {
            getResourceTypesAndNames($langCodesStore[0], [...otResourceCodes_, ...ntResourceCodes_])
              .then((resourceTypesAndNames) => {
                // Filter down to the resource type provided by the user
                filteredResourceTypesAndNames = resourceTypesAndNames.filter(
                  (element: [string, string, string]) => {
                    return element[0] === langCode && element[1] === resource
                  }
                )
                console.log(`filteredResourceTypesAndNames: ${filteredResourceTypesAndNames}`)
                if (filteredResourceTypesAndNames.length > 0) {
                  $resourceTypesStore.push(
                    `${filteredResourceTypesAndNames[0][0]}, ${filteredResourceTypesAndNames[0][1]}, ${filteredResourceTypesAndNames[0][2]}`
                  )
                  console.log(`$resourceTypesStore: ${$resourceTypesStore}`)
                  $resourceTypesCountStore = 1
                } else {
                  console.log('filteredResourceTypesAndNames was empty')
                }
                routeToPage('/settings')
              })
              .catch((err) => console.error(err))
          }
        } else {
          message = `Unfortunately, you've requested a language code, ${langCode}, which is not available.`
          console.log('filteredLangCodeNameAndTypes was empty')
        }
      })
      .catch((err) => console.log(err))
  } else if (components.length === 2) {
    // e.g., repo_url=https:%2F%2Fcontent.bibletranslationtools.org%2FWycliffeAssociates%2Fen_ulb
    langCode = components[0]
    if (components[1] === 'ulb') {
      resource = 'ulb-wa'
    } else {
      resource = components[1]
    }
    console.log(
      `Transferred values from BIEL, langCode: ${langCode}, all books, resource: ${resource}`
    )
    message = `You've requested the following values, langCode: ${langCode}, all books, resource: ${resource}`
    getLangCodesNames()
      .then((langCodeNameAndTypes_) => {
        // Save result for later use
        langCodeNameAndTypes = langCodeNameAndTypes_
        filteredLangCodeNameAndTypes = langCodeNameAndTypes_.filter(
          (element: [string, string, boolean]) => {
            return element[0] === langCode
          }
        )
        console.log(`filteredLangCodeNameAndTypes: ${filteredLangCodeNameAndTypes}`)
        if (filteredLangCodeNameAndTypes.length > 0) {
          $langCodesStore.push(filteredLangCodeNameAndTypes[0][0])
          $langNamesStore.push(filteredLangCodeNameAndTypes[0][1])
          if (filteredLangCodeNameAndTypes[0][2]) {
            $gatewayCodeAndNamesStore.push(
              `${filteredLangCodeNameAndTypes[0][0]}, ${filteredLangCodeNameAndTypes[0][1]}`
            )
          } else {
            $heartCodeAndNamesStore.push(
              `${filteredLangCodeNameAndTypes[0][0]}, ${filteredLangCodeNameAndTypes[0][1]}`
            )
          }
          $langCountStore = 1
          // Add all Old Testament books to ot book store
          for (var bookCode of otBooks) {
            $otBookStore.push(`${bookCode}, ${booksMap[bookCode]}`)
            // console.log(`$otBookStore: ${otBookStore}`)
          }
          // Add all New Testament books to nt book store
          for (var bookCode of ntBooks) {
            $ntBookStore.push(`${bookCode}, ${booksMap[bookCode]}`)
            // console.log(`$ntBookStore: ${$ntBookStore}`)
          }
          $bookCountStore = otBooks.length + ntBooks.length
          let otResourceCodes_: Array<[string, string]> = $otBookStore.map((item) => [
            getCode(item),
            getName(item)
          ])
          let ntResourceCodes_: Array<[string, string]> = $ntBookStore.map((item) => [
            getCode(item),
            getName(item)
          ])
          if ($langCodesStore[0]) {
            getResourceTypesAndNames($langCodesStore[0], [
              ...otResourceCodes_,
              ...ntResourceCodes_
            ]).then((resourceTypesAndNames) => {
              // Filter down to the resource type provided by the user
              filteredResourceTypesAndNames = resourceTypesAndNames.filter(
                (element: [string, string, string]) => {
                  return element[0] === langCode && element[1] === resource
                }
              )
              console.log(`filteredResourceTypesAndNames: ${filteredResourceTypesAndNames}`)
              if (filteredResourceTypesAndNames.length > 0) {
                $resourceTypesStore.push(
                  `${filteredResourceTypesAndNames[0][0]}, ${filteredResourceTypesAndNames[0][1]}, ${filteredResourceTypesAndNames[0][2]}`
                )
                console.log(`$resourceTypesStore: ${$resourceTypesStore}`)
                $resourceTypesCountStore = 1
              } else {
                console.log('filteredResourceTypesAndNames was empty')
              }
              routeToPage('/settings')
              // NOTE This case is for the whole bible, e.g., en_ulb. But
              // we could conceivably redirect the user to the books route
              // to choose their books since we don't typically want to produce an
              // entire bible due to poor performance on a document that huge.
              // routeToPage('/books')
            })
          }
        }
      })
      .catch((err) => console.log(err))
  } else {
    errorMessage =
      "We're sorry the information transferred from bibleineverylanguage.org is not available in this system. Please contact support."
    console.log(`repo url: ${data.repo}`)
    console.log(`components of transfer url: ${components}`)
  }

  $: console.log(`$langCodesStore: ${$langCodesStore}`)
  $: console.log(`$langNamesStore: ${$langNamesStore}`)
  $: console.log(`$langCountStore: ${$langCountStore}`)
  $: console.log(`$resourceTypesStore: ${$resourceTypesStore}`)
  $: console.log(`$resourceTypesCountStore: ${$resourceTypesCountStore}`)
  $: console.log(`$otBookStore: ${$otBookStore}`)
  $: console.log(`$ntBookStore: ${$ntBookStore}`)
  $: console.log(`$bookCountStore: ${$bookCountStore}`)
</script>

<div class="ml-8 mt-8 text-[#33445C]">
  <div class="p-4">
    <p>{message}</p>
  </div>
  {#if !errorMessage}
    <div class="mt-4 p-4">
      <p>
        We are initializing and validating your request so far, this will take a few moments and
        then you will be transferred to the review page...
      </p>
    </div>
    <div class="mt-4 p-4">
      <ProgressIndicator />
    </div>
  {:else}
    <div class="mt-4 p-4">
      <p>{errorMessage}</p>
    </div>
  {/if}
</div>
