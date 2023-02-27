<script lang="ts">
  import { push } from 'svelte-spa-router'
  // The dumbed-down version and the full version of the app each
  // maintain their own stores since they are stateful and you
  // don't want a user navigating from the dumbed-down version
  // of the app to the full version to share state between them.
  import {
    lang0CodeStore,
    lang1CodeStore,
    langCountStore
  } from '../../stores/v1_release/LanguagesStore_v1'
  import { otBookStore, ntBookStore, bookCountStore } from '../../stores/v1_release/BooksStore_v1'
  import {
    lang0ResourceTypesStore,
    lang1ResourceTypesStore,
    resourceTypesCountStore
  } from '../../stores/v1_release/ResourceTypesStore_v1'
  import {
    layoutForPrintStore,
    assemblyStrategyKindStore,
    assemblyStrategyChunkSizeStore,
    docTypeStore,
    generatePdfStore,
    generateEpubStore,
    generateDocxStore,
    emailStore,
    documentRequestKeyStore
  } from '../../stores/v1_release/SettingsStore_v1'
  import { documentReadyStore, errorStore } from '../../stores/v1_release/NotificationStore_v1'
  import { taskIdStore, taskStateStore } from '../../stores/v1_release/TaskStore_v1'
  import { getApiRootUrl, resetStores, printToConsole } from '../../lib/v1_release/utils_v1'

  // ------------------------------------------------------------
  // BEGIN: Code for v1 release that normally lives in
  // ResourceTypes.svelte, but must live here now that
  // we choose the resource types for the user automatically
  // in this basic version.

  async function getResourceTypesAndNames(
    langCode: string,
    resourceCodeAndNames: Array<[string, string]>,
    apiRootUrl = getApiRootUrl(),
    sharedResourceTypesUrl = <string>import.meta.env.VITE_SHARED_RESOURCE_TYPES_URL_V1
  ): Promise<Array<[string, string]>> {
    // NOTE Form the URL to ultimately invoke
    // resource_lookup.shared_resource_types.
    const url_ = `${apiRootUrl}${sharedResourceTypesUrl}${langCode}/`
    const url = new URL(url_)
    resourceCodeAndNames.map(resourceCodeAndName =>
      url.searchParams.append('resource_codes', resourceCodeAndName[0])
    )
    printToConsole(`url: ${url}`)
    const response = await fetch(url)
    const resourceTypesAndNames: Array<[string, string]> = await response.json()
    if (!response.ok) {
      printToConsole(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }

    return resourceTypesAndNames
  }

  // Resolve promise for data for language 0
  let lang0ResourceTypesAndNames: Array<string>
  $: {
    if ($lang0CodeStore && ($otBookStore.length > 0 || $ntBookStore.length > 0)) {
      printToConsole(`$otBookStore: ${$otBookStore}`)
      let otResourceCodes_: Array<[string, string]> = $otBookStore.map(item => [
        item.split(', ')[0],
        item.split(', ')[1]
      ])
      printToConsole(`$ntBookStore: ${$ntBookStore}`)
      let ntResourceCodes_: Array<[string, string]> = $ntBookStore.map(item => [
        item.split(', ')[0],
        item.split(', ')[1]
      ])
      getResourceTypesAndNames($lang0CodeStore, [
        ...otResourceCodes_,
        ...ntResourceCodes_
      ])
        .then(resourceTypesAndNames => {
          printToConsole("About to set lang0ResourceTypesAndNames using getResourceTypesAndNames for lang0")
          lang0ResourceTypesAndNames = resourceTypesAndNames.map(
            tuple => `${tuple[0]}, ${tuple[1]}`
          )
        })
        .catch(err => console.error(err))
    }
  }

  // Resolve promise for data for language 1
  let lang1ResourceTypesAndNames: Array<string>
  $: {
    if ($lang1CodeStore && ($otBookStore.length > 0 || $ntBookStore.length > 0)) {
      let otResourceCodes_: Array<[string, string]> = $otBookStore.map(item => [
        item.split(', ')[0],
        item.split(', ')[1]
      ])
      let ntResourceCodes_: Array<[string, string]> = $ntBookStore.map(item => [
        item.split(', ')[0],
        item.split(', ')[1]
      ])
      getResourceTypesAndNames($lang1CodeStore, [
        ...otResourceCodes_,
        ...ntResourceCodes_
      ])
        .then(resourceTypesAndNames => {
          printToConsole("About to set lang1ResourceTypesAndNames using getResourceTypesAndNames for lang1")
          lang1ResourceTypesAndNames = resourceTypesAndNames.map(
            tuple => `${tuple[0]}, ${tuple[1]}`
          )
        })
        .catch(err => console.error(err))
    }
  }

  // Store lang0ResourceTypesAndNames codes into
  // lang0ResourceTypesStore here.
  $: {
    if (lang0ResourceTypesAndNames) {
      printToConsole("Updating lang0ResourceTypesStore")
      lang0ResourceTypesStore.set(lang0ResourceTypesAndNames)
      printToConsole(`lang0ResourceTypesStore: ${lang0ResourceTypesStore}`)
    }
  }

  // Store lang1ResourceTypesAndNames codes into
  // lang1ResourceTypesStore here.
  $: {
    if (lang1ResourceTypesAndNames) {
      printToConsole("Updating lang1ResourceTypesStore")
      lang1ResourceTypesStore.set(lang1ResourceTypesAndNames)
      printToConsole(`lang1ResourceTypesStore: ${lang1ResourceTypesStore}`)
    }
  }

  $: printToConsole(`lang0ResourceTypesAndNames: ${lang0ResourceTypesAndNames}`)
  $: printToConsole(`lang1ResourceTypesAndNames: ${lang1ResourceTypesAndNames}`)
  $: {
    if (lang0ResourceTypesAndNames) {
      lang0ResourceTypesAndNames.map(resourceTypeAndName => printToConsole(`resourceTypeAndName: ${resourceTypeAndName}`))
    }
  }
  $: {
    if (lang1ResourceTypesAndNames) {
      lang1ResourceTypesAndNames.map(resourceTypeAndName => printToConsole(`resourceTypeAndName: ${resourceTypeAndName}`))
    }
  }


  // Keep track of how many resources are currently stored reactively.
  let nonEmptyLang0Resourcetypes: boolean
  $: nonEmptyLang0Resourcetypes = $lang0ResourceTypesStore.every(item => item.length > 0)

  let nonEmptyLang1Resourcetypes: boolean
  $: nonEmptyLang1Resourcetypes = $lang1ResourceTypesStore.every(item => item.length > 0)

  $: {
    if (nonEmptyLang0Resourcetypes && nonEmptyLang1Resourcetypes) {
      resourceTypesCountStore.set(
        $lang0ResourceTypesStore.length + $lang1ResourceTypesStore.length
      )
    } else if (nonEmptyLang0Resourcetypes && !nonEmptyLang1Resourcetypes) {
      resourceTypesCountStore.set($lang0ResourceTypesStore.length)
    } else if (!nonEmptyLang0Resourcetypes && nonEmptyLang1Resourcetypes) {
      resourceTypesCountStore.set($lang1ResourceTypesStore.length)
    } else {
      resourceTypesCountStore.set(0)
    }
    printToConsole(`resourceTypesCountStore: ${resourceTypesCountStore}`)
  }
  // END relevant ResourceTypes.svelte logic ------------------------

  let apiRootUrl = getApiRootUrl()

  function reset() {
    resetStores('languages')
    resetStores('books')
    resetStores('resource_types')
    resetStores('settings')
    resetStores('notifications')
  }

  async function poll(taskId: string): Promise<string | [string, string]> {
    printToConsole(`taskId in poll: ${taskId}`)
    let res = await fetch(`${apiRootUrl}/task_status/${taskId}`, {
      method: 'GET'
    })
    let json = await res.json()
    let state = json?.state
    if (state === 'SUCCESS') {
      let result = json?.result
      return [state, result]
    }
    return state
  }

  async function generateDocument() {
    let rr = []
    let resourceCodes = [...$otBookStore, ...$ntBookStore]
    // Create resource_requests for lang0
    for (let resourceCode of resourceCodes) {
      for (let resourceType of $lang0ResourceTypesStore) {
        rr.push({
          lang_code: $lang0CodeStore,
          resource_type: resourceType.split(', ')[0],
          resource_code: resourceCode.split(', ')[0]
        })
      }
    }
    // Create resource_requests for lang1
    for (let resourceCode of resourceCodes) {
      for (let resourceType of $lang1ResourceTypesStore) {
        rr.push({
          lang_code: $lang1CodeStore,
          resource_type: resourceType.split(', ')[0],
          resource_code: resourceCode.split(', ')[0]
        })
      }
    }

    // Deal with empty string case
    if ($emailStore && $emailStore === '') {
      emailStore.set(null)
      // Deal with undefined case
    } else if ($emailStore === undefined) {
      emailStore.set(null)
      // Deal with non-empty string
    } else if ($emailStore && $emailStore !== '') {
      emailStore.set($emailStore.trim())
    }

    // For v1 release, we set the value in docTypeStore here as we
    // don't allow the user to choose the output type for the v1 release.
    // Because we haven't solved the issue of embedding fonts in the Word
    // template, we had better default for PDF for now since some
    // gateway languages even need special fonts. But the actual
    // requirement is to default to Docx.
    // TODO Solve special fonts availability in Word for languages
    // that need it after which we can switch this to docx instead of
    // pdf.
    $docTypeStore = <string>import.meta.env.VITE_V1_OUTPUT_FORMAT
    // For v1 release, we set the value of assemblyStrategyKindStore
    // and layoutForPrintStore here as we
    // don't allow the user to choose the output type for the v1 release.
    $assemblyStrategyKindStore = 'lbo'
    $layoutForPrintStore = false

    if ($docTypeStore === 'pdf') {
      $generatePdfStore = true
      $generateEpubStore = false
      $generateDocxStore = false
    } else if ($docTypeStore === 'epub') {
      $generatePdfStore = false
      $generateEpubStore = true
      $generateDocxStore = false
    } else if ($docTypeStore === 'docx') {
      $generatePdfStore = false
      $generateEpubStore = false
      $generateDocxStore = true
    }
    // Create the JSON structure to POST.
    let documentRequest = {
      email_address: $emailStore,
      assembly_strategy_kind: $assemblyStrategyKindStore,
      layout_for_print: $layoutForPrintStore,
      generate_pdf: $generatePdfStore,
      generate_epub: $generateEpubStore,
      generate_docx: $generateDocxStore,
      resource_requests: rr
    }
    printToConsole(`document request: ${JSON.stringify(documentRequest, null, 2)}`)
    push('#/v1/result')
    errorStore.set(null)
    documentReadyStore.set(false)
    documentRequestKeyStore.set('')
    let endpointUrl = "documents"
    if ($generateDocxStore) {
      endpointUrl = "documents_docx"
    }
    const response = await fetch(`${apiRootUrl}/${endpointUrl}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(documentRequest)
    })
    const data = await response.json()
    if (!response.ok) {
      console.error(`data.detail: ${data.detail}`)
      errorStore.set(data.detail)
    } else {
      printToConsole(`data: ${JSON.stringify(data)}`)
      $taskIdStore = data.task_id
      printToConsole(`$taskIdStore: ${$taskIdStore}`)
      const timer = setInterval(async function () {
        // Poll the server for the task state and result, if ready
        let results = await poll($taskIdStore)
        printToConsole(`results: ${results}`)
        $taskStateStore = Array.isArray(results) ? results[0] : results
        printToConsole(`$taskStateStore: ${$taskStateStore}`)
        if ($taskStateStore === 'SUCCESS' && Array.isArray(results) && results[1]) {
          let finishedDocumentRequestKey = results[1]
          printToConsole(`finishedDocumentReuestKey: ${finishedDocumentRequestKey}`)
          documentReadyStore.set(true)
          documentRequestKeyStore.set(finishedDocumentRequestKey)
          errorStore.set(null)
          taskStateStore.set('')
          clearInterval(timer)
        } else if ($taskStateStore === 'FAILURE') {
          printToConsole("We're sorry, an internal error occurred which we'll investigate.")
          errorStore.set(
            "We're sorry. An error occurred. The document you requested may not yet be supported or we may have experienced an internal problem which we'll investigate. Please try another document request."
          )
          taskStateStore.set('')
          clearInterval(timer)
        }
      }, 5000)
    }
  }

  $: printToConsole(`$lang0CodeStore: ${$lang0CodeStore}`)
  $: printToConsole(`$lang1CodeStore: ${$lang1CodeStore}`)
  $: printToConsole(`$langCountStore: ${$langCountStore}`)
  $: printToConsole(`$assemblyStrategyKindStore: ${$assemblyStrategyKindStore}`)
  $: printToConsole(`$bookCountStore: ${$bookCountStore}`)
  $: printToConsole(`$resourceTypesCountStore: ${$resourceTypesCountStore}`)


</script>

<div class="text-center h-28 bg-white pt-8 pb-4">
  {#if ($langCountStore > 0 || $langCountStore <= 2) && $assemblyStrategyKindStore && $bookCountStore > 0 && $resourceTypesCountStore > 0}
    <div class="pb-4">
      <button
        class="btn orange-gradient w-5/6 rounded"
        on:click={() => generateDocument()}
      >
        <span class="py-2 px-4 text-secondary-content capitalize">Generate Document</span>
      </button>
    </div>
    <!-- <div class="pb-4"> -->
    <!--   <button -->
    <!--     class="btn gray-gradiant hover:focus:gray-gradiant w-5/6 text-neutral-content rounded capitalize" -->
    <!--     on:click={() => reset()}>Reset</button -->
    <!--   > -->
    <!-- </div> -->
  {:else}
    <div class="pb-4">
      <button class="btn  btn-disabled gray-gradiant w-5/6 rounded">
        <span class="py-2 px-4 text-secondary-content capitalize" style="color: #140E0866"
          >Generate Document</span
        >
      </button>
    </div>
  {/if}
</div>

<style global lang="postcss">
  * :global(.gray-gradiant) {
    background: linear-gradient(0deg, rgba(20, 14, 8, 0.05), rgba(20, 14, 8, 0.05)),
      linear-gradient(0deg, rgba(20, 14, 8, 0), rgba(20, 14, 8, 0));
    /* background: linear-gradient(0deg, rgba(20, 14, 8, 0.2), rgba(20, 14, 8, 0.2)), */
    /*   linear-gradient(0deg, rgba(20, 14, 8, 0.05), rgba(20, 14, 8, 0.05)); */
  }

  * :global(.orange-gradient) {
    background: linear-gradient(180deg, #fdd231 0%, #fdad29 100%),
      linear-gradient(0deg, rgba(20, 14, 8, 0.6), rgba(20, 14, 8, 0.6));
  }
</style>
