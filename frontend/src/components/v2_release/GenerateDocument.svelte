<script lang="ts">
  import DownloadButton from './DownloadButton.svelte'
  import { documentReadyStore, errorStore } from '../../stores/v2_release/NotificationStore'
  import {
    langCodesStore,
    langCountStore
  } from '../../stores/v2_release/LanguagesStore'
  import { otBookStore, ntBookStore, bookCountStore } from '../../stores/v2_release/BooksStore'
  import {
    resourceTypesStore,
    resourceTypesCountStore
  } from '../../stores/v2_release/ResourceTypesStore'
  import {
    layoutForPrintStore,
    assemblyStrategyKindStore,
    docTypeStore,
    generatePdfStore,
    generateEpubStore,
    generateDocxStore,
    emailStore,
    documentRequestKeyStore,
    limitTwStore
  } from '../../stores/v2_release/SettingsStore'
  import { taskIdStore, taskStateStore } from '../../stores/v2_release/TaskStore'
  import { getApiRootUrl, getFileServerUrl, getResourceTypeLangCode } from '../../lib/utils'
  import LogRocket from 'logrocket'
  import ProgressIndicator from './ProgressIndicator.svelte'

  let apiRootUrl = getApiRootUrl()
  let fileServerUrl: string = getFileServerUrl()

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

  $: generatingDocument = false

  async function generateDocument() {
    generatingDocument = true
    let rr = []
    let resourceCodes = [...$otBookStore, ...$ntBookStore]
    // Create resource_requests for lang0
    for (let resourceCode of resourceCodes) {
      for (let resourceType of $resourceTypesStore) {
        if (getResourceTypeLangCode(resourceType) === $langCodesStore[0]) {
          rr.push({
            lang_code: $langCodesStore[0],
            resource_type: resourceType.split(', ')[1],
            resource_code: resourceCode.split(', ')[0]
          })
        }
      }
    }
    // Create resource_requests for lang1
    if ($langCountStore > 1) {
      for (let resourceCode of resourceCodes) {
        for (let resourceType of $resourceTypesStore) {
          if (getResourceTypeLangCode(resourceType) === $langCodesStore[1]) {
            rr.push({
              lang_code: $langCodesStore[1],
              resource_type: resourceType.split(', ')[1],
              resource_code: resourceCode.split(', ')[0]
            })
          }
        }
      }
    }

    // Deal with empty string case
    if ($emailStore && $emailStore === '') {
      emailStore.set(null)
      LogRocket.identify($documentRequestKeyStore)
      // Deal with undefined case
    } else if ($emailStore === undefined) {
      emailStore.set(null)
      LogRocket.identify($documentRequestKeyStore)
      // Deal with non-empty string
    } else if ($emailStore && $emailStore !== '') {
      emailStore.set($emailStore.trim())
      // The LogRocket init call has been moved to App.svelte to be earlier in
      // the loading process so that hopefully more of the session
      // is recorded.
      // Send email to LogRocket using identify session.
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


  let pdfDownloadUrl: string
  $: pdfDownloadUrl = `${fileServerUrl}/${$documentRequestKeyStore}.pdf`
  let ePubDownloadUrl: string
  $: ePubDownloadUrl = `${fileServerUrl}/${$documentRequestKeyStore}.epub`
  let docxDownloadUrl: string
  $: docxDownloadUrl = `${fileServerUrl}/${$documentRequestKeyStore}.docx`
  let htmlDownloadUrl: string
  $: htmlDownloadUrl = `${fileServerUrl}/${$documentRequestKeyStore}.html`

  function viewFromUrl(url: string) {
    console.log(`url: ${url}`)
    window.open(url, '_blank')
  }
</script>

<div class="h-28 bg-white pt-12 pb-4">
  {#if !generatingDocument}
    {#if ($langCountStore > 0 || $langCountStore <= 2) && $assemblyStrategyKindStore && $bookCountStore > 0 && $resourceTypesCountStore > 0}
      <div class="pb-4">
        <button
          class="text-center p-4 blue-gradient w-1/2 rounded-md"
          on:click={() => generateDocument()}
        >
          <span class="text-white">Generate File</span>
        </button>
      </div>
    {:else}
      <div class="pb-4">
        <button class="text-center p-4 btn-disabled gray-gradiant w-1/2 rounded-md">
          <span class="text-[#B3B9C2]" style="color: #140E0866"
            >Generate File</span
          >
        </button>
      </div>
    {/if}
  {:else}
    {#if !$documentReadyStore && !$errorStore}
      <div class="flex">
        {#if $taskStateStore === "Locating assets"}
          <div class="h-1 w-1/2 bg-[#F2F3F5]">
            <div class="h-1 blue-gradient-bar" style="width: 5%"></div>
          </div>
        {:else if $taskStateStore === "Provisioning asset files"}
          <div class="h-1 w-1/2 bg-[#F2F3F5]">
            <div class="h-1 blue-gradient-bar" style="width: 10%"></div>
          </div>
        {:else if $taskStateStore === "Parsing asset files"}
          <div class="h-1 w-1/2 bg-[#F2F3F5]">
            <div class="h-1 blue-gradient-bar" style="width: 20%"></div>
          </div>
        {:else if $taskStateStore === "Assembling content"}
          <div class="h-1 w-1/2 bg-[#F2F3F5]">
            <div class="h-1 blue-gradient-bar" style="width: 50%"></div>
          </div>
        {:else if $taskStateStore === "Provisioning USFM asset files for TW resource"}
          <div class="h-1 w-1/2 bg-[#F2F3F5]">
            <div class="h-1 blue-gradient-bar" style="width: 55%"></div>
          </div>
        {:else if $taskStateStore === "Parsing USFM asset files for TW resource"}
          <div class="h-1 w-1/2 bg-[#F2F3F5]">
            <div class="h-1 blue-gradient-bar" style="width: 60%"></div>
          </div>
        {:else if $taskStateStore === "Limiting TW words"}
          <div class="h-1 w-1/2 bg-[#F2F3F5]">
            <div class="h-1 blue-gradient-bar" style="width: 65%"></div>
          </div>
        {:else if $taskStateStore === "Converting to PDF" ||
          $taskStateStore === "Converting to ePub" || $taskStateStore
          === "Converting to Docx"}
          <div class="h-1 w-1/2 bg-[#F2F3F5]">
            <div class="h-1 blue-gradient-bar" style="width: 70%"></div>
          </div>
        {:else}
          <div class="h-1 w-1/2 bg-[#F2F3F5]">
            <div class="h-1 blue-gradient-bar" style="width: 0%"></div>
          </div>
        {/if}
      </div>
      {#if $taskStateStore}
        <p id="state" class="text-[#B3B9C2]">
          <ProgressIndicator labelString={$taskStateStore} />
        </p>
      {/if}
    {/if}
    {#if $documentReadyStore && !$errorStore}
      <div class="bg-white">
          <div class="h-1 w-1/2 bg-[#F2F3F5]">
            <div class="h-1 blue-gradient-bar" style="width: 100%"></div>
          </div>
        <div class="m-auto"><h3 class="text-[#82A93F]">Complete!</h3></div>
        {#if $generatePdfStore}
          <div class="m-auto mt-4">
            <DownloadButton buttonText="Download PDF" url={pdfDownloadUrl} />
          </div>
        {/if}
        {#if $generateEpubStore}
          <div class="m-auto mt-4">
            <DownloadButton buttonText="Download ePub" url={ePubDownloadUrl} />
          </div>
        {/if}
        {#if $generateDocxStore}
          <div class="m-auto mt-4">
            <DownloadButton buttonText="Download Docx" url={docxDownloadUrl} />
          </div>
          <div class="text-secondary-content mt-4">
            <p>
            Any missing fonts on your computer may be downloaded here:
            <span style="text-decoration-line: underline;">
              <a href="https://github.com/Bible-Translation-Tools/ScriptureAppBuilder-pipeline/tree/base/ContainerImage/home/fonts"
                target="_blank">fonts</a>
            </span>
            </p>
          </div>
          <div class="text-secondary-content mt-4">
            <p>
              Once you have downloaded and installed any missing fonts,
              select the document text which looks like little empty boxes
              (indicating a missing font), and change the font for that
              highlighted text to the appropriate installed font in
              Word, then save the Word document.
            </p>
          </div>
        {/if}
        {#if !$generateDocxStore}
          <div class="mt-4 pb-4">
            <button
              class="border-2 border-[#e5e8eb] p-4 text-center gray-gradient hover:gray-gradient-hover w-1/2 rounded-md"
              on:click={() => viewFromUrl(htmlDownloadUrl)}
            >
              <svg
                class="m-auto"
                width="23"
                height="16"
                viewBox="0 0 23 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M11.5 0.5C6.5 0.5 2.23 3.61 0.5 8C2.23 12.39 6.5 15.5 11.5 15.5C16.5 15.5 20.77 12.39 22.5 8C20.77 3.61 16.5 0.5 11.5 0.5ZM11.5 13C8.74 13 6.5 10.76 6.5 8C6.5 5.24 8.74 3 11.5 3C14.26 3 16.5 5.24 16.5 8C16.5 10.76 14.26 13 11.5 13ZM11.5 5C9.84 5 8.5 6.34 8.5 8C8.5 9.66 9.84 11 11.5 11C13.16 11 14.5 9.66 14.5 8C14.5 6.34 13.16 5 11.5 5Z"
                  fill="#1A130B"
                  fill-opacity="0.8"
                />
              </svg>
              <span class="p-4">View HTML Online</span>
            </button>
          </div>
        {/if}
      </div>
    {:else}
      <button class="text-center bg-[#F2F3F5] border border-[#E5E8EB]
                     hover:bg-[#efefef] p-4 w-1/2 rounded-md
                     text-[#B3B9C2] mt-2 mb-4" disabled>
          Download
      </button>
      <p class="text-[#B3B9C2] mt-4 italic">
          We appreciate your patience as this can take several minutes for larger documents.
      </p>
    {/if}
    {#if $errorStore}
      <div class="bg-white">
        <svg
          class="m-auto"
          width="44"
          height="38"
          viewBox="0 0 44 38"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M24 24H20V14H24V24ZM24 32H20V28H24V32ZM0 38H44L22 0L0 38Z"
            fill="#B85659"
          />
        </svg>
        <div class="m-auto"><h3 class="text-[#B85659] text-center">Uh Oh...</h3></div>
        <div class="m-auto">
          <p class="text-[#B3B9C2]">
            Something went wrong. Please review your selections or contact tech support for
            assistance.
          </p>
        </div>
      </div>
    {/if}
  {/if}

</div>

<style>
  * :global(.gray-gradiant) {
    background: linear-gradient(0deg, rgba(20, 14, 8, 0.05), rgba(20, 14, 8, 0.05)),
      linear-gradient(0deg, rgba(20, 14, 8, 0), rgba(20, 14, 8, 0));
  }
  * :global(.gray-gradient:hover) {
    background: linear-gradient(0deg, rgba(20, 14, 8, 0.3), rgba(20, 14, 8, 0.3)),
      linear-gradient(0deg, rgba(20, 14, 8, 0.05), rgba(20, 14, 8, 0.05));
  }
  * :global(.blue-gradient) {
    background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%),
    linear-gradient(0deg, #33445C, #33445C);
  }
  * :global(.blue-gradient-bar) {
    background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);
  }

</style>
