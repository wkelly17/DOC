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
    generatePdfStore,
    generateEpubStore,
    generateDocxStore,
    emailStore,
    documentRequestKeyStore
  } from '../stores/SettingsStore'
  import { documentReadyStore, errorStore } from '../stores/NotificationStore'
  import { getApiRootUrl, resetStores } from '../lib/utils'

  let apiRootUrl = getApiRootUrl()

  function reset() {
    resetStores('languages')
    resetStores('books')
    resetStores('resource_types')
    resetStores('settings')
    resetStores('notifications')
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
    console.log('document request: ', JSON.stringify(documentRequest, null, 2))
    push('#/result')
    errorStore.set(null)
    documentReadyStore.set(false)
    documentRequestKeyStore.set('')
    const response = await fetch(`${apiRootUrl}/documents`, {
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
      documentReadyStore.set(true)
      documentRequestKeyStore.set(data['finished_document_request_key'])
      errorStore.set(null)
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
