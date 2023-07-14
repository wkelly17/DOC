<script lang="ts">
  import { push } from 'svelte-spa-router'
  import {
    lang0CodeStore,
    lang1CodeStore,
    langCountStore
  } from '../stores/LanguagesStore'
  import { otBookStore, ntBookStore, bookCountStore } from '../stores/BooksStore'
  import {
    lang0ResourceTypesStore,
    lang1ResourceTypesStore,
    resourceTypesCountStore
  } from '../stores/ResourceTypesStore'
  import {
    layoutForPrintStore,
    assemblyStrategyKindStore,
    assemblyStrategyChunkSizeStore,
    docTypeStore,
    generatePdfStore,
    generateEpubStore,
    generateDocxStore,
    emailStore,
    documentRequestKeyStore,
    limitTwStore
  } from '../stores/SettingsStore'
  import { documentReadyStore, errorStore } from '../stores/NotificationStore'
  import { taskIdStore, taskStateStore } from '../stores/TaskStore'
  import { getApiRootUrl, resetStores } from '../lib/utils'
  import LogRocket from 'logrocket'


  let apiRootUrl = getApiRootUrl()

  function reset() {
    resetStores('languages')
    resetStores('books')
    resetStores('resource_types')
    resetStores('settings')
    resetStores('notifications')
  }

  async function poll(taskId: string): Promise<string | [string, string]> {
    console.log(`taskId in poll: ${taskId}`)
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
      // Send email to LogRocket using identify
      LogRocket.init('ct7zyg/interleaved-resource-generator')
      LogRocket.identify($emailStore)
    }

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
      resource_requests: rr,
      document_request_source: "ui",
      limit_words: $limitTwStore
    }
    console.log('document request: ', JSON.stringify(documentRequest, null, 2))
    push('#/experimental/result')
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
      console.log(`data: ${JSON.stringify(data)}`)
      $taskIdStore = data.task_id
      console.log(`$taskIdStore: ${$taskIdStore}`)
      const timer = setInterval(async function () {
        // Poll the server for the task state and result, if ready
        let results = await poll($taskIdStore)
        console.log(`results: ${results}`)
        $taskStateStore = Array.isArray(results) ? results[0] : results
        console.log(`$taskStateStore: ${$taskStateStore}`)
        if ($taskStateStore === 'SUCCESS' && Array.isArray(results) && results[1]) {
          let finishedDocumentRequestKey = results[1]
          console.log(`finishedDocumentReuestKey: ${finishedDocumentRequestKey}`)
          documentReadyStore.set(true)
          documentRequestKeyStore.set(finishedDocumentRequestKey)
          errorStore.set(null)
          taskStateStore.set('')
          clearInterval(timer)
        } else if ($taskStateStore === 'FAILURE') {
          console.log("We're sorry, an internal error occurred which we'll investigate.")
          errorStore.set(
            "We're sorry. An error occurred. The document you requested may not yet be supported or we may have experienced an internal problem which we'll investigate. Please try another document request."
          )
          taskStateStore.set('')
          clearInterval(timer)
        }
      }, 5000)
    }
  }
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
