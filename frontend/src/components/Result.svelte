<script lang="ts">
  import { ProgressRing } from 'fluent-svelte'
  import DownloadButton from './DownloadButton.svelte'
  import { push } from 'svelte-spa-router'
  import { documentReadyStore, errorStore } from '../stores/NotificationStore'
  import LeftArrow from './LeftArrow.svelte'
  import {
    generatePdfStore,
    generateEpubStore,
    generateDocxStore,
    documentRequestKeyStore
  } from '../stores/SettingsStore'
  import { taskIdStore, taskStateStore } from '../stores/TaskStore'
  import { getApiRootUrl, getFileServerUrl, resetStores } from '../lib/utils'
  import Mast from './Mast.svelte'
  import Tabs from './Tabs.svelte'
  import Sidebar from './Sidebar.svelte'
  import { setShowTopMatter } from '../lib/utils'

  function cancelDocument() {
    console.log('Called cancelDocument')
    resetStores('languages')
    resetStores('books')
    resetStores('resource_types')
    resetStores('settings')
    resetStores('notifications')
    push('#/experimental')
  }

  let apiRootUrl: string = getApiRootUrl()
  let fileServerUrl: string = getFileServerUrl()

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


  // For sidebar
  let open = false
  let showTopMatter: boolean = setShowTopMatter()
</script>

{#if showTopMatter}
<Sidebar bind:open />
<Mast bind:sidebar="{open}" />
<Tabs />
{/if}

<div class="bg-white flex">
  <button
    class="bg-white hover:bg-grey-100 text-primary-content font-bold py-2 px-4 rounded inline-flex items-center"
    on:click={() => push('#/experimental')}
  >
    <LeftArrow backLabel="Go Back" />
  </button>
</div>
<div class="bg-white m-auto w-full px-2 pt-2 mt-2">
  {#if !$documentReadyStore && !$errorStore}
    <h3 class="text-center text-secondary-content">Your document is being generated.</h3>
    <div class="flex justify-center">
      <ProgressRing />
    </div>
    <p class="text-center text-secondary-content">
      We appreciate your patience as this can take several minutes for larger documents.
    </p>
    {#if $taskIdStore}
      <p class="text-center text-secondary-content">
        Task id: {$taskIdStore}
      </p>
    {/if}
    {#if $taskStateStore}
      <p id="state" class="text-center  text-secondary-content">
        Task state: {$taskStateStore}
      </p>
    {/if}
  {/if}
  {#if $documentReadyStore && !$errorStore}
    <div class="bg-white">
      <svg
        class="m-auto"
        width="20"
        height="16"
        viewBox="0 0 20 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M2 8L8 14L18 2"
          stroke="#82A93F"
          stroke-width="2.66667"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      <div class="m-auto"><h3 class="text-[#82A93F] text-center">Success!</h3></div>
      <p class="text-center text-secondary-content">
        Your document was generated successfully. You may {#if
          $generatePdfStore || $generateEpubStore ||
        $generateDocxStore}download it{/if}{#if !$generateDocxStore}&nbsp; or view it online{/if}.
      </p>
      {#if $generatePdfStore}
        <div class="m-auto text-center mt-4">
          <DownloadButton buttonText="Download PDF" url={pdfDownloadUrl} />
        </div>
      {/if}
      {#if $generateEpubStore}
        <div class="m-auto text-center mt-4">
          <DownloadButton buttonText="Download ePub" url={ePubDownloadUrl} />
        </div>
      {/if}
      {#if $generateDocxStore}
        <div class="m-auto text-center mt-4">
          <DownloadButton buttonText="Download Docx" url={docxDownloadUrl} />
        </div>
        <div class="text-center text-secondary-content mt-4">
          <p>
          Any missing fonts on your computer may be downloaded here:
          <span style="text-decoration-line: underline;">
            <a href="https://github.com/Bible-Translation-Tools/ScriptureAppBuilder-pipeline/tree/base/ContainerImage/home/fonts"
               target="_blank">fonts</a>
          </span>
          </p>
        </div>
        <div class="text-center text-secondary-content mt-4">
          <p>
            Once you have downloaded and installed any missing fonts,
            select the document text which looks like little empty boxes
            (indicating a missing font), and change the font for that
            highlighted text to the appropriate installed font in
            Word, then save the Word document.
          </p>
        </div>
        <!-- <div class="text-center text-secondary-content mt-4"> -->
        <!--   <p> -->
        <!--     You may want to turn off spell checking in Word also as -->
        <!--     multi-language Word documents can cause spell check to run -->
        <!--     excessively. -->
        <!--   </p> -->
        <!-- </div> -->
      {/if}
      {#if !$generateDocxStore}
      <div class="m-auto text-center mt-4">
        <button
          class="btn gray-gradient hover:gray-gradient-hover w-5/6 rounded capitalize"
          on:click={() => viewFromUrl(htmlDownloadUrl)}
        >
          <svg
            class="rm-3"
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
          View HTML Online</button
        >
      </div>
      {/if}
    </div>
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
        <p class="text-center text-secondary-content">
          Something went wrong. Please review your selections or contact tech support for
          assistance.
        </p>
      </div>
    </div>
  {/if}
</div>

{#if !$documentReadyStore && !$errorStore}
  <div class="text-center bg-white px-2 pt-2 mt-2">
    <button
      on:click|preventDefault={cancelDocument}
      class="btn w-5/6 gray-gradient capitalize">Cancel</button
    >
  </div>
{/if}

<style global lang="postcss">
  * :global(.gray-gradient) {
    background: linear-gradient(0deg, rgba(20, 14, 8, 0.2), rgba(20, 14, 8, 0.2)),
      linear-gradient(0deg, rgba(20, 14, 8, 0.05), rgba(20, 14, 8, 0.05));
  }
  * :global(.gray-gradient:hover) {
    background: linear-gradient(0deg, rgba(20, 14, 8, 0.3), rgba(20, 14, 8, 0.3)),
      linear-gradient(0deg, rgba(20, 14, 8, 0.05), rgba(20, 14, 8, 0.05));
  }
</style>
