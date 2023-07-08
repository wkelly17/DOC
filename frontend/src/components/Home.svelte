<script lang="ts">
  import { glLangCodeAndNamesStore, nonGlLangCodeAndNamesStore, langCountStore } from '../stores/LanguagesStore'
  import { otBookStore, ntBookStore, bookCountStore } from '../stores/BooksStore'
  import {
    lang0ResourceTypesStore,
    lang1ResourceTypesStore,
    resourceTypesCountStore
  } from '../stores/ResourceTypesStore'
  import { resetValuesStore } from '../stores/NotificationStore'
  import {emailStore} from '../stores/SettingsStore'
  import { push } from 'svelte-spa-router'
  import GenerateDocument from './GenerateDocument.svelte'
  import RightArrow from './RightArrow.svelte'
  import Mast from './Mast.svelte'
  import Tabs from './Tabs.svelte'
  import Sidebar from './Sidebar.svelte'
  import { setShowTopMatter } from '../lib/utils'
  import { printToConsole } from '../lib/v1_release/utils_v1'

  // Handle notification of reset of values originating from other
  // pages.
  let showResetValuesMessage: boolean = false
  $: {
    if ($resetValuesStore) {
      showResetValuesMessage = true
    }
  }

  $: console.log(`$glLangCodeAndNamesStore: ${$glLangCodeAndNamesStore}`)
  $: console.log(`$nonGlLangCodeAndNamesStore: ${$nonGlLangCodeAndNamesStore}`)
  $: console.log(`glLangNames: ${glLangNames}`)
  $: console.log(`nonGlLangNames: ${nonGlLangNames}`)
  $: console.log(`$resetValuesStore: ${$resetValuesStore}`)


  // Get the language names from the store reactively.
  $: glLangNames = $glLangCodeAndNamesStore.map(
    langCodeAndName => langCodeAndName.split(", ")[1]
  )
  $: nonGlLangNames = $nonGlLangCodeAndNamesStore.map(
    langCodeAndName => langCodeAndName.split(", ")[1]
  )

  const numLangsToShow = 5
  $: glLangNamesAbbr = glLangNames.slice(0, numLangsToShow)
  $: nonGlLangNamesAbbr = nonGlLangNames.slice(0, numLangsToShow)

  // Get the book names from the store reactively.
  $: otBookNames = $otBookStore.map(
    resourceCodeAndName => resourceCodeAndName.split(', ')[1]
  )
  $: ntBookNames = $ntBookStore.map(
    resourceCodeAndName => resourceCodeAndName.split(', ')[1]
  )

  const numBooksToShow = 5
  $: otBookNamesAbbr = otBookNames.slice(0, numBooksToShow)
  $: ntBookNamesAbbr = ntBookNames.slice(0, numBooksToShow)

  $: lang0ResourceTypeNames = $lang0ResourceTypesStore.map(
    resourceTypeAndName => resourceTypeAndName.split(', ')[1]
  )
  $: lang1ResourceTypeNames = $lang1ResourceTypesStore.map(
    resourceTypeAndName => resourceTypeAndName.split(', ')[1]
  )

  const numResourceTypesToShow = 3
  $: lang0ResourceTypeNamesAbbr = lang0ResourceTypeNames.slice(0, numResourceTypesToShow)
  $: lang1ResourceTypeNamesAbbr = lang1ResourceTypeNames.slice(0, numResourceTypesToShow)

  let glLangsDisplayString: string = ''
  $: {
    if (glLangNames && glLangNames.length > numLangsToShow) {
      glLangsDisplayString = `${glLangNamesAbbr.join(', ')}...`
    } else if (
      glLangNames &&
      glLangNames.length > 0 &&
      glLangNames.length <= numLangsToShow
    ) {
      glLangsDisplayString = glLangNames.join(', ')
    }
  }

  let nonGlLangsDisplayString: string = ''
  $: {
    if (nonGlLangNames && nonGlLangNames.length > numLangsToShow) {
      nonGlLangsDisplayString = `${nonGlLangNamesAbbr.join(', ')}...`
    } else if (
      nonGlLangNames &&
      nonGlLangNames.length > 0 &&
      nonGlLangNames.length <= numLangsToShow
    ) {
      nonGlLangsDisplayString = nonGlLangNames.join(', ')
    }
  }
  $: console.log(`glLangsDisplayString: ${glLangsDisplayString}`)
  $: console.log(`nonGlLangsDisplayString: ${nonGlLangsDisplayString}`)

  let langsDisplayString: string = ''
  $: {
    if (glLangNames.length > 0 && nonGlLangNames.length > 0) {
      langsDisplayString = `${[glLangsDisplayString, nonGlLangsDisplayString]}`
    } else if (glLangNames.length > 0 && nonGlLangNames.length === 0) {
      langsDisplayString = glLangsDisplayString
    } else if (glLangNames.length === 0 && nonGlLangNames.length > 0) {
      langsDisplayString = nonGlLangsDisplayString
    }
  }

  let otBooksDisplayString: string = ''
  $: {
    if (otBookNames && otBookNames.length > numBooksToShow) {
      otBooksDisplayString = `${otBookNamesAbbr.join(', ')}...`
    } else if (
      otBookNames &&
      otBookNames.length > 0 &&
      otBookNames.length <= numBooksToShow
    ) {
      otBooksDisplayString = otBookNames.join(', ')
    }
  }

  let ntBooksDisplayString: string = ''
  $: {
    if (ntBookNames && ntBookNames.length > numBooksToShow) {
      ntBooksDisplayString = `${ntBookNamesAbbr.join(', ')}...`
    } else if (
      ntBookNames &&
      ntBookNames.length > 0 &&
      ntBookNames.length <= numBooksToShow
    ) {
      ntBooksDisplayString = ntBookNames.join(', ')
    }
  }

  let booksDisplayString: string = ''
  $: {
    if (otBookNames.length > 0 && ntBookNames.length > 0) {
      booksDisplayString = `${[otBooksDisplayString, ntBooksDisplayString]}`
    } else if (otBookNames.length > 0 && ntBookNames.length === 0) {
      booksDisplayString = otBooksDisplayString
    } else if (otBookNames.length === 0 && ntBookNames.length > 0) {
      booksDisplayString = ntBooksDisplayString
    }
  }
  let lang0ResourceTypesDisplayString: string = ''
  let lang1ResourceTypesDisplayString: string = ''
  let resourceTypesDisplayString: string = ''
  $: {
    // Update for the first language
    if (
      lang0ResourceTypeNames &&
      lang0ResourceTypeNames.length > numResourceTypesToShow
    ) {
      lang0ResourceTypesDisplayString = `${lang0ResourceTypeNamesAbbr.join(', ')}...`
    } else {
      lang0ResourceTypesDisplayString = lang0ResourceTypeNames.join(', ')
    }

    // Update for the second language
    if (
      lang1ResourceTypeNames &&
      lang1ResourceTypeNames.length > numResourceTypesToShow
    ) {
      lang1ResourceTypesDisplayString = `${lang1ResourceTypeNamesAbbr.join(', ')}...`
    } else {
      lang1ResourceTypesDisplayString = lang1ResourceTypeNames.join(', ')
    }

    // Update for both languages in combination
    if (lang0ResourceTypesDisplayString && lang1ResourceTypesDisplayString) {
      resourceTypesDisplayString = `${lang0ResourceTypesDisplayString}, ${lang1ResourceTypesDisplayString}`
    } else {
      resourceTypesDisplayString = lang0ResourceTypesDisplayString
    }
  }

  $: printToConsole(`resourceTypesDisplayString: ${resourceTypesDisplayString}`)

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

  // For sidebar
  let open = false
  let showTopMatter: boolean = setShowTopMatter()
  $: console.log(`showTopMatter: ${showTopMatter}`)
</script>

{#if showTopMatter}
<Sidebar bind:open />
<Mast bind:sidebar="{open}" />
<Tabs />
{/if}

<div class="bg-white">
  <ul>
    <li class="bg-white border-b-2 border-grey-500 p-2">
      <button
        class="inline-flex items-center w-full justify-between py-2 px-4 rounded"
        on:click={() => push('#/experimental/languages')}
      >
        <div class="flex items-center">
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M14.36 12C14.44 11.34 14.5 10.68 14.5 10C14.5 9.32 14.44 8.66 14.36 8H17.74C17.9 8.64 18 9.31 18 10C18 10.69 17.9 11.36 17.74 12H14.36ZM12.59 17.56C13.19 16.45 13.65 15.25 13.97 14H16.92C15.9512 15.6683 14.4141 16.932 12.59 17.56ZM12.34 12H7.66C7.56 11.34 7.5 10.68 7.5 10C7.5 9.32 7.56 8.65 7.66 8H12.34C12.43 8.65 12.5 9.32 12.5 10C12.5 10.68 12.43 11.34 12.34 12ZM10 17.96C9.17 16.76 8.5 15.43 8.09 14H11.91C11.5 15.43 10.83 16.76 10 17.96ZM6 6H3.08C4.03886 4.32721 5.5748 3.06149 7.4 2.44C6.8 3.55 6.35 4.75 6 6ZM3.08 14H6C6.35 15.25 6.8 16.45 7.4 17.56C5.57862 16.9317 4.04485 15.6677 3.08 14ZM2.26 12C2.1 11.36 2 10.69 2 10C2 9.31 2.1 8.64 2.26 8H5.64C5.56 8.66 5.5 9.32 5.5 10C5.5 10.68 5.56 11.34 5.64 12H2.26ZM10 2.03C10.83 3.23 11.5 4.57 11.91 6H8.09C8.5 4.57 9.17 3.23 10 2.03ZM16.92 6H13.97C13.657 4.76146 13.1936 3.5659 12.59 2.44C14.43 3.07 15.96 4.34 16.92 6ZM10 0C4.47 0 0 4.5 0 10C0 12.6522 1.05357 15.1957 2.92893 17.0711C3.85752 17.9997 4.95991 18.7362 6.17317 19.2388C7.38642 19.7413 8.68678 20 10 20C12.6522 20 15.1957 18.9464 17.0711 17.0711C18.9464 15.1957 20 12.6522 20 10C20 8.68678 19.7413 7.38642 19.2388 6.17317C18.7362 4.95991 17.9997 3.85752 17.0711 2.92893C16.1425 2.00035 15.0401 1.26375 13.8268 0.761205C12.6136 0.258658 11.3132 0 10 0Z"
              fill="#140E08"
              fill-opacity="0.6"
            />
          </svg>
          <span class="ml-4 font-bold text-secondary-content text-xl">1. Languages</span>
        </div>
        <RightArrow />
      </button>
      {#if $langCountStore > 0}
        <div>
          <span class="text-neutral-content text-sm ml-14 capitalize">
            {langsDisplayString}
          </span>
        </div>
      {:else}
        <div>
          <span class="text-neutral-content text-sm ml-14">Select languages</span>
        </div>
      {/if}
    </li>
    <li class="bg-white border-b-2 border-grey-500 p-2">
      <button
        class="inline-flex items-center w-full justify-between py-2 px-4 rounded"
        on:click={() => push('#/experimental/books')}
      >
        <div class="flex items-center">
          <svg
            width="16"
            height="20"
            viewBox="0 0 16 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M14 20C14.5304 20 15.0391 19.7893 15.4142 19.4142C15.7893 19.0391 16 18.5304 16 18V2C16 1.46957 15.7893 0.960859 15.4142 0.585786C15.0391 0.210714 14.5304 0 14 0H8V7L5.5 5.5L3 7V0H2C1.46957 0 0.960859 0.210714 0.585786 0.585786C0.210714 0.960859 0 1.46957 0 2V18C0 18.5304 0.210714 19.0391 0.585786 19.4142C0.960859 19.7893 1.46957 20 2 20H14Z"
              fill="#140E08"
            />
          </svg>
          {#if $bookCountStore > 0}
            <span class="ml-4 font-bold text-xl text-secondary-content">2. Books</span>
          {:else}
            <span class="ml-4 text-xl text-neutral-content">2. Books</span>
          {/if}
        </div>
        <RightArrow />
      </button>
      {#if $bookCountStore > 0}
        <div>
          <span class="text-neutral-content text-sm ml-14 capitalize"
            >{booksDisplayString}</span
          >
        </div>
      {:else}
        <div>
          <span class="text-neutral-content text-sm ml-14">Select books</span>
        </div>
      {/if}
    </li>
    <li class="bg-white p-2">
      <button
        class="inline-flex items-center w-full justify-between  py-2 px-4 rounded"
        on:click={() => push('#/experimental/resource_types')}
      >
        <div class="flex items-center">
          <svg
            width="16"
            height="20"
            viewBox="0 0 16 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M2 0C1.46957 0 0.960859 0.210714 0.585786 0.585786C0.210714 0.960859 0 1.46957 0 2V18C0 18.5304 0.210714 19.0391 0.585786 19.4142C0.960859 19.7893 1.46957 20 2 20H14C14.5304 20 15.0391 19.7893 15.4142 19.4142C15.7893 19.0391 16 18.5304 16 18V6L10 0H2ZM2 2H9V7H14V18H2V2ZM4 10V12H12V10H4ZM4 14V16H9V14H4Z"
              fill="#140E08"
              fill-opacity="0.6"
            />
          </svg>
          {#if $resourceTypesCountStore > 0}
            <span class="ml-4 font-bold text-xl text-secondary-content"
              >3. Resource types</span
            >
          {:else}
            <span class="ml-4 text-xl text-neutral-content">3. Resource types</span>
          {/if}
        </div>
        <RightArrow />
      </button>
      {#if $resourceTypesCountStore > 0}
        <div>
          <span class="text-neutral-content text-sm ml-14 capitalize"
            >{resourceTypesDisplayString}
          </span>
        </div>
      {:else}
        <div>
          <span class="text-neutral-content text-sm ml-14">Select resource types</span>
        </div>
      {/if}
    </li>
    <li class="bg-white p-2">
      <div class="flex justify-between">
        <!-- <label for="email" class="text-primary-content" -->
        <!--        >{import.meta.env.VITE_EMAIL_LABEL}</label -->
        <!--                                             > -->
        <input
          type="text"
          name="email"
          id="email"
          bind:value="{$emailStore}"
          placeholder="Type email address here (optional)"
          class="input input-bordered bg-white w-full max-w-xs"
          />
      </div>
      <div>
        <span class="text-sm text-neutral-content"
              >Providing an email is optional and not required. Providing an email address allows us to stay in
          touch regarding system updates and proactively provide support should
          we notice you ran into any issues.</span
                                                             >
      </div>
    </li>
  </ul>
  <GenerateDocument />
  <!-- NOTE For unsophisticated users and for users whose language is not -->
  <!-- English it might be wise not to show a toast or modal and instead -->
  <!-- just carry out the action. The system is designed such that they -->
  <!-- will be guided to the correct result anyway without the message  -->
  <!-- which might be more confusing to such a user than no message at all. -->
  <!-- {#if showResetValuesMessage} -->
  <!--   <div class="toast toast-center toast-middle"> -->
  <!--     <div class="alert alert-info"> -->
  <!--       <div> -->
  <!--         <span> -->
  <!--           Languages, books, resource types, and settings are interdependent. Since -->
  <!--           you've made a change here, we've reset your other values to ensure you create -->
  <!--           a valid document. Now you can continue on to books to make your selections. -->
  <!--         </span> -->
  <!--       </div> -->
  <!--     </div> -->
  <!--   </div> -->
  <!-- {/if} -->
  <!-- NOTE We need to use a modal instead of a toast so that we can use the -->
  <!-- 'Ok' button to trigger an event which we catch to set the value of -->
  <!-- resetValuesMessageStore.set(false) -->
  <!-- {#if showResetValuesMessage} -->
  <!--   <input type="checkbox" id="my-modal" class="modal-toggle" checked /> -->
  <!--   <div class="modal"> -->
  <!--     <div class="modal-box"> -->
  <!--       <h3 class="text-primary-content font-bold text-lg">Info message:</h3> -->
  <!--       <p class="py-4 text-primary-content"> -->
  <!--         Languages, books, resource types, and settings are interdependent. Since you've -->
  <!--         made a change here, we've reset your other values to ensure you create a valid -->
  <!--         document. Now you can continue on to books to make your selections. -->
  <!--       </p> -->
  <!--       <div class="modal-action"> -->
  <!--         <label for="my-modal" class="btn" on:click={() => resetValuesStore.set(false)} -->
  <!--           >Ok</label -->
  <!--         > -->
  <!--       </div> -->
  <!--     </div> -->
  <!--   </div> -->
  <!-- {/if} -->
</div>
