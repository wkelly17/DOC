<script lang="ts">
  import { push, location } from 'svelte-spa-router'
  import {
    glLangCodeAndNamesStore,
    nonGlLangCodeAndNamesStore,
  } from '../../stores/v2_release/LanguagesStore'
  import { bookCountStore, ntBookStore, otBookStore } from '../../stores/v2_release/BooksStore'
  import {
    lang0ResourceTypesStore,
    lang1ResourceTypesStore,
    resourceTypesCountStore
  } from '../../stores/v2_release/ResourceTypesStore'
  import { langRegExp, bookRegExp, resourceTypeRegExp, settingsRegExp } from '../../lib/utils'

  function uncheckGlLanguage(langCodeAndName: string) {
    glLangCodeAndNamesStore.set($glLangCodeAndNamesStore.filter(item => item != langCodeAndName))
  }
  function uncheckNonGlLanguage(langCodeAndName: string) {
    nonGlLangCodeAndNamesStore.set($nonGlLangCodeAndNamesStore.filter(item => item != langCodeAndName))
  }
  function uncheckBook(bookCodeAndName: string) {
    otBookStore.set($otBookStore.filter(item => item != bookCodeAndName))
    ntBookStore.set($ntBookStore.filter(item => item != bookCodeAndName))
  }
  function uncheckLang0ResourceType(resourceTypeCodeAndName: string) {
    lang0ResourceTypesStore.set($lang0ResourceTypesStore.filter(item => item != resourceTypeCodeAndName))
  }
  function uncheckLang1ResourceType(resourceTypeCodeAndName: string) {
    lang1ResourceTypesStore.set($lang1ResourceTypesStore.filter(item => item != resourceTypeCodeAndName))
  }

  // Slice the collection of books into the first 'size' amount and
  // the remainder so that the UI can display size + 1 to end of
  // collection amount of books in a collapsed accordion control.
  let size = 5
  $: allBooks = [...$otBookStore, ...$ntBookStore]
  $: shownBooks = allBooks.slice(0, size)
  $: hiddenBooks = allBooks.slice(size, -1)

</script>


  <div class="flex-shrink-0 w-1/3 p-4 overflow-y-auto bg-[#f2f3f5]">
    <h1 class="pl-0 py-4 font-semibold text-xl text-[#33445C]">Your Selection</h1>
    {#if langRegExp.test($location)}
      <div class="flex items-center my-2">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M16.36 14C16.44 13.34 16.5 12.68 16.5 12C16.5 11.32 16.44 10.66 16.36 10H19.74C19.9 10.64 20 11.31 20 12C20 12.69 19.9 13.36 19.74 14H16.36ZM14.59 19.56C15.19 18.45 15.65 17.25 15.97 16H18.92C17.9512 17.6683 16.4141 18.932 14.59 19.56ZM14.34 14H9.66C9.56 13.34 9.5 12.68 9.5 12C9.5 11.32 9.56 10.65 9.66 10H14.34C14.43 10.65 14.5 11.32 14.5 12C14.5 12.68 14.43 13.34 14.34 14ZM12 19.96C11.17 18.76 10.5 17.43 10.09 16H13.91C13.5 17.43 12.83 18.76 12 19.96ZM8 8H5.08C6.03886 6.32721 7.5748 5.06149 9.4 4.44C8.8 5.55 8.35 6.75 8 8ZM5.08 16H8C8.35 17.25 8.8 18.45 9.4 19.56C7.57862 18.9317 6.04485 17.6677 5.08 16ZM4.26 14C4.1 13.36 4 12.69 4 12C4 11.31 4.1 10.64 4.26 10H7.64C7.56 10.66 7.5 11.32 7.5 12C7.5 12.68 7.56 13.34 7.64 14H4.26ZM12 4.03C12.83 5.23 13.5 6.57 13.91 8H10.09C10.5 6.57 11.17 5.23 12 4.03ZM18.92 8H15.97C15.657 6.76146 15.1936 5.5659 14.59 4.44C16.43 5.07 17.96 6.34 18.92 8ZM12 2C6.47 2 2 6.5 2 12C2 14.6522 3.05357 17.1957 4.92893 19.0711C5.85752 19.9997 6.95991 20.7362 8.17317 21.2388C9.38642 21.7413 10.6868 22 12 22C14.6522 22 17.1957 20.9464 19.0711 19.0711C20.9464 17.1957 22 14.6522 22 12C22 10.6868 21.7413 9.38642 21.2388 8.17317C20.7362 6.95991 19.9997 5.85752 19.0711 4.92893C18.1425 4.00035 17.0401 3.26375 15.8268 2.7612C14.6136 2.25866 13.3132 2 12 2Z" fill="#001533"/>
        </svg>
        <h2 class="ml-2 font-semibold text-xl text-[#33445C]">Language</h2>
      </div>
    {:else}
      <div class="flex items-center justify-between my-2">
        <div class="flex items-center justify-between">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16.36 14C16.44 13.34 16.5 12.68 16.5 12C16.5 11.32 16.44 10.66 16.36 10H19.74C19.9 10.64 20 11.31 20 12C20 12.69 19.9 13.36 19.74 14H16.36ZM14.59 19.56C15.19 18.45 15.65 17.25 15.97 16H18.92C17.9512 17.6683 16.4141 18.932 14.59 19.56ZM14.34 14H9.66C9.56 13.34 9.5 12.68 9.5 12C9.5 11.32 9.56 10.65 9.66 10H14.34C14.43 10.65 14.5 11.32 14.5 12C14.5 12.68 14.43 13.34 14.34 14ZM12 19.96C11.17 18.76 10.5 17.43 10.09 16H13.91C13.5 17.43 12.83 18.76 12 19.96ZM8 8H5.08C6.03886 6.32721 7.5748 5.06149 9.4 4.44C8.8 5.55 8.35 6.75 8 8ZM5.08 16H8C8.35 17.25 8.8 18.45 9.4 19.56C7.57862 18.9317 6.04485 17.6677 5.08 16ZM4.26 14C4.1 13.36 4 12.69 4 12C4 11.31 4.1 10.64 4.26 10H7.64C7.56 10.66 7.5 11.32 7.5 12C7.5 12.68 7.56 13.34 7.64 14H4.26ZM12 4.03C12.83 5.23 13.5 6.57 13.91 8H10.09C10.5 6.57 11.17 5.23 12 4.03ZM18.92 8H15.97C15.657 6.76146 15.1936 5.5659 14.59 4.44C16.43 5.07 17.96 6.34 18.92 8ZM12 2C6.47 2 2 6.5 2 12C2 14.6522 3.05357 17.1957 4.92893 19.0711C5.85752 19.9997 6.95991 20.7362 8.17317 21.2388C9.38642 21.7413 10.6868 22 12 22C14.6522 22 17.1957 20.9464 19.0711 19.0711C20.9464 17.1957 22 14.6522 22 12C22 10.6868 21.7413 9.38642 21.2388 8.17317C20.7362 6.95991 19.9997 5.85752 19.0711 4.92893C18.1425 4.00035 17.0401 3.26375 15.8268 2.7612C14.6136 2.25866 13.3132 2 12 2Z" fill="#001533"/>
          </svg>
          <h2 class="ml-2 font-semibold text-xl text-[#33445C]">Language</h2>
        </div>
        <button class="flex bg-white text-[#33445c] hover:bg-[#efefef] py-2 px-4 rounded" on:click={() => push("/v2/languages")}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 17.4624V20.5024C3 20.7824 3.22 21.0024 3.5 21.0024H6.54C6.67 21.0024 6.8 20.9524 6.89 20.8524L17.81 9.94244L14.06 6.19244L3.15 17.1024C3.05 17.2024 3 17.3224 3 17.4624ZM20.71 7.04244C20.8027 6.94993 20.8762 6.84004 20.9264 6.71907C20.9766 6.59809 21.0024 6.46841 21.0024 6.33744C21.0024 6.20648 20.9766 6.07679 20.9264 5.95582C20.8762 5.83485 20.8027 5.72496 20.71 5.63244L18.37 3.29244C18.2775 3.19974 18.1676 3.12619 18.0466 3.07601C17.9257 3.02583 17.796 3 17.665 3C17.534 3 17.4043 3.02583 17.2834 3.07601C17.1624 3.12619 17.0525 3.19974 16.96 3.29244L15.13 5.12244L18.88 8.87244L20.71 7.04244Z" fill="#33445C"/>
          </svg>
          <span class="ml-2">
          Edit
          </span>
        </button>
      </div>
    {/if}
    {#if (($glLangCodeAndNamesStore && $glLangCodeAndNamesStore.length > 0) || ($nonGlLangCodeAndNamesStore && $nonGlLangCodeAndNamesStore.length > 0))}
      {#each $glLangCodeAndNamesStore as langCodeAndName}
          {#if langRegExp.test($location)}
            <div class="flex items-center justify-between w-full rounded-lg p-4 bg-white text-[#66768B] mt-2">{langCodeAndName.split(/, (.*)/s)[1]}
              <button on:click={() => uncheckGlLanguage(langCodeAndName)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.47 2 2 6.47 2 12C2 17.53 6.47 22 12 22C17.53 22 22 17.53 22 12C22 6.47 17.53 2 12 2ZM16.3 16.3C16.2075 16.3927 16.0976 16.4663 15.9766 16.5164C15.8557 16.5666 15.726 16.5924 15.595 16.5924C15.464 16.5924 15.3343 16.5666 15.2134 16.5164C15.0924 16.4663 14.9825 16.3927 14.89 16.3L12 13.41L9.11 16.3C8.92302 16.487 8.66943 16.592 8.405 16.592C8.14057 16.592 7.88698 16.487 7.7 16.3C7.51302 16.113 7.40798 15.8594 7.40798 15.595C7.40798 15.4641 7.43377 15.3344 7.48387 15.2135C7.53398 15.0925 7.60742 14.9826 7.7 14.89L10.59 12L7.7 9.11C7.51302 8.92302 7.40798 8.66943 7.40798 8.405C7.40798 8.14057 7.51302 7.88698 7.7 7.7C7.88698 7.51302 8.14057 7.40798 8.405 7.40798C8.66943 7.40798 8.92302 7.51302 9.11 7.7L12 10.59L14.89 7.7C14.9826 7.60742 15.0925 7.53398 15.2135 7.48387C15.3344 7.43377 15.4641 7.40798 15.595 7.40798C15.7259 7.40798 15.8556 7.43377 15.9765 7.48387C16.0975 7.53398 16.2074 7.60742 16.3 7.7C16.3926 7.79258 16.466 7.90249 16.5161 8.02346C16.5662 8.14442 16.592 8.27407 16.592 8.405C16.592 8.53593 16.5662 8.66558 16.5161 8.78654C16.466 8.90751 16.3926 9.01742 16.3 9.11L13.41 12L16.3 14.89C16.68 15.27 16.68 15.91 16.3 16.3Z" fill="#33445C"/>
                </svg>
              </button>
            </div>
          {:else}
            <div class="flex items-center justify-between w-full rounded-lg p-4 bg-white text-[#66768B] mt-2">{langCodeAndName.split(/, (.*)/s)[1]}</div>
         {/if}
      {/each}
      {#each $nonGlLangCodeAndNamesStore as langCodeAndName}
        {#if langRegExp.test($location)}
          <div class="flex items-center justify-between w-full rounded-lg p-4 bg-white text-[#66768B] mt-2">{langCodeAndName.split(/, (.*)/s)[1]}
            <button on:click={() => uncheckNonGlLanguage(langCodeAndName)}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.47 2 2 6.47 2 12C2 17.53 6.47 22 12 22C17.53 22 22 17.53 22 12C22 6.47 17.53 2 12 2ZM16.3 16.3C16.2075 16.3927 16.0976 16.4663 15.9766 16.5164C15.8557 16.5666 15.726 16.5924 15.595 16.5924C15.464 16.5924 15.3343 16.5666 15.2134 16.5164C15.0924 16.4663 14.9825 16.3927 14.89 16.3L12 13.41L9.11 16.3C8.92302 16.487 8.66943 16.592 8.405 16.592C8.14057 16.592 7.88698 16.487 7.7 16.3C7.51302 16.113 7.40798 15.8594 7.40798 15.595C7.40798 15.4641 7.43377 15.3344 7.48387 15.2135C7.53398 15.0925 7.60742 14.9826 7.7 14.89L10.59 12L7.7 9.11C7.51302 8.92302 7.40798 8.66943 7.40798 8.405C7.40798 8.14057 7.51302 7.88698 7.7 7.7C7.88698 7.51302 8.14057 7.40798 8.405 7.40798C8.66943 7.40798 8.92302 7.51302 9.11 7.7L12 10.59L14.89 7.7C14.9826 7.60742 15.0925 7.53398 15.2135 7.48387C15.3344 7.43377 15.4641 7.40798 15.595 7.40798C15.7259 7.40798 15.8556 7.43377 15.9765 7.48387C16.0975 7.53398 16.2074 7.60742 16.3 7.7C16.3926 7.79258 16.466 7.90249 16.5161 8.02346C16.5662 8.14442 16.592 8.27407 16.592 8.405C16.592 8.53593 16.5662 8.66558 16.5161 8.78654C16.466 8.90751 16.3926 9.01742 16.3 9.11L13.41 12L16.3 14.89C16.68 15.27 16.68 15.91 16.3 16.3Z" fill="#33445C"/>
              </svg>
            </button>
          </div>
        {:else}
          <div class="flex items-center justify-between w-full rounded-lg p-4 bg-white text-[#66768B] mt-2">{langCodeAndName.split(/, (.*)/s)[1]}</div>
        {/if}
      {/each}
    {:else}
      <div class="rounded-lg p-6 bg-[#e5e8eb] text-[#66768b]">Selections will appear here once a language is selected</div>
    {/if}
    {#if !bookRegExp.test($location) && $bookCountStore > 0}
      <div class="flex items-center justify-between my-2">
        <div class="flex items-center justify-between">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 22C5.45 22 4.97933 21.8043 4.588 21.413C4.196 21.021 4 20.55 4 20V4C4 3.45 4.196 2.979 4.588 2.587C4.97933 2.19567 5.45 2 6 2H18C18.55 2 19.021 2.19567 19.413 2.587C19.8043 2.979 20 3.45 20 4V20C20 20.55 19.8043 21.021 19.413 21.413C19.021 21.8043 18.55 22 18 22H6ZM6 20H18V4H16V10.125C16 10.325 15.9167 10.4707 15.75 10.562C15.5833 10.654 15.4167 10.65 15.25 10.55L13.5 9.5L11.75 10.55C11.5833 10.65 11.4167 10.654 11.25 10.562C11.0833 10.4707 11 10.325 11 10.125V4H6V20ZM11 4H16H11ZM6 4H18H6Z" fill="#001533"/>
          </svg>
          <h2 class="ml-2 font-semibold text-xl text-[#33445C]">Book</h2>
        </div>
        <button class="flex bg-white text-[#33445c] hover:bg-[#efefef] py-2 px-4 rounded" on:click={() => push("/v2/books")}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 17.4624V20.5024C3 20.7824 3.22 21.0024 3.5 21.0024H6.54C6.67 21.0024 6.8 20.9524 6.89 20.8524L17.81 9.94244L14.06 6.19244L3.15 17.1024C3.05 17.2024 3 17.3224 3 17.4624ZM20.71 7.04244C20.8027 6.94993 20.8762 6.84004 20.9264 6.71907C20.9766 6.59809 21.0024 6.46841 21.0024 6.33744C21.0024 6.20648 20.9766 6.07679 20.9264 5.95582C20.8762 5.83485 20.8027 5.72496 20.71 5.63244L18.37 3.29244C18.2775 3.19974 18.1676 3.12619 18.0466 3.07601C17.9257 3.02583 17.796 3 17.665 3C17.534 3 17.4043 3.02583 17.2834 3.07601C17.1624 3.12619 17.0525 3.19974 16.96 3.29244L15.13 5.12244L18.88 8.87244L20.71 7.04244Z" fill="#33445C"/>
          </svg>
          Edit
        </button>
      </div>
    {:else}
      <div class="flex items-center my-2">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M6 22C5.45 22 4.97933 21.8043 4.588 21.413C4.196 21.021 4 20.55 4 20V4C4 3.45 4.196 2.979 4.588 2.587C4.97933 2.19567 5.45 2 6 2H18C18.55 2 19.021 2.19567 19.413 2.587C19.8043 2.979 20 3.45 20 4V20C20 20.55 19.8043 21.021 19.413 21.413C19.021 21.8043 18.55 22 18 22H6ZM6 20H18V4H16V10.125C16 10.325 15.9167 10.4707 15.75 10.562C15.5833 10.654 15.4167 10.65 15.25 10.55L13.5 9.5L11.75 10.55C11.5833 10.65 11.4167 10.654 11.25 10.562C11.0833 10.4707 11 10.325 11 10.125V4H6V20ZM11 4H16H11ZM6 4H18H6Z" fill="#001533"/>
        </svg>
        <h2 class="ml-2 font-semibold text-xl text-[#33445C]">Book</h2>
      </div>
    {/if}
    {#if $bookCountStore > 0}
      {#each shownBooks as bookCodeAndName}
        {#if bookRegExp.test($location)}
          <div class="flex items-center justify-between w-full rounded-lg p-4 bg-white text-[#66768B] mt-2">{bookCodeAndName.split(/, (.*)/s)[1]}
            <button on:click={() => uncheckBook(bookCodeAndName)}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.47 2 2 6.47 2 12C2 17.53 6.47 22 12 22C17.53 22 22 17.53 22 12C22 6.47 17.53 2 12 2ZM16.3 16.3C16.2075 16.3927 16.0976 16.4663 15.9766 16.5164C15.8557 16.5666 15.726 16.5924 15.595 16.5924C15.464 16.5924 15.3343 16.5666 15.2134 16.5164C15.0924 16.4663 14.9825 16.3927 14.89 16.3L12 13.41L9.11 16.3C8.92302 16.487 8.66943 16.592 8.405 16.592C8.14057 16.592 7.88698 16.487 7.7 16.3C7.51302 16.113 7.40798 15.8594 7.40798 15.595C7.40798 15.4641 7.43377 15.3344 7.48387 15.2135C7.53398 15.0925 7.60742 14.9826 7.7 14.89L10.59 12L7.7 9.11C7.51302 8.92302 7.40798 8.66943 7.40798 8.405C7.40798 8.14057 7.51302 7.88698 7.7 7.7C7.88698 7.51302 8.14057 7.40798 8.405 7.40798C8.66943 7.40798 8.92302 7.51302 9.11 7.7L12 10.59L14.89 7.7C14.9826 7.60742 15.0925 7.53398 15.2135 7.48387C15.3344 7.43377 15.4641 7.40798 15.595 7.40798C15.7259 7.40798 15.8556 7.43377 15.9765 7.48387C16.0975 7.53398 16.2074 7.60742 16.3 7.7C16.3926 7.79258 16.466 7.90249 16.5161 8.02346C16.5662 8.14442 16.592 8.27407 16.592 8.405C16.592 8.53593 16.5662 8.66558 16.5161 8.78654C16.466 8.90751 16.3926 9.01742 16.3 9.11L13.41 12L16.3 14.89C16.68 15.27 16.68 15.91 16.3 16.3Z" fill="#33445C"/>
              </svg>
            </button>
          </div>
        {:else}
          <div class="flex items-center justify-between w-full rounded-lg p-4 bg-white text-[#66768B] mt-2">{bookCodeAndName.split(/, (.*)/s)[1]}</div>
        {/if}
      {/each}
      <!-- Put remainder books in a collapsed accordion that can be expanded -->
      {#if hiddenBooks.length > 0}
        <div class="collapse collapse-arrow w-full rounded-lg bg-white text-[#66768B] mt-2">
          <input type="checkbox" />
          <div class="collapse-title">
            ({hiddenBooks.length}) items hidden
          </div>
          <div class="collapse-content">
            {#each hiddenBooks as bookCodeAndName}
              {#if bookRegExp.test($location)}
                <div class="flex items-center justify-between w-full rounded-lg  bg-white text-[#66768B] p-2 mt-2">{bookCodeAndName.split(/, (.*)/s)[1]}
                  <button on:click={() => uncheckBook(bookCodeAndName)}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2C6.47 2 2 6.47 2 12C2 17.53 6.47 22 12 22C17.53 22 22 17.53 22 12C22 6.47 17.53 2 12 2ZM16.3 16.3C16.2075 16.3927 16.0976 16.4663 15.9766 16.5164C15.8557 16.5666 15.726 16.5924 15.595 16.5924C15.464 16.5924 15.3343 16.5666 15.2134 16.5164C15.0924 16.4663 14.9825 16.3927 14.89 16.3L12 13.41L9.11 16.3C8.92302 16.487 8.66943 16.592 8.405 16.592C8.14057 16.592 7.88698 16.487 7.7 16.3C7.51302 16.113 7.40798 15.8594 7.40798 15.595C7.40798 15.4641 7.43377 15.3344 7.48387 15.2135C7.53398 15.0925 7.60742 14.9826 7.7 14.89L10.59 12L7.7 9.11C7.51302 8.92302 7.40798 8.66943 7.40798 8.405C7.40798 8.14057 7.51302 7.88698 7.7 7.7C7.88698 7.51302 8.14057 7.40798 8.405 7.40798C8.66943 7.40798 8.92302 7.51302 9.11 7.7L12 10.59L14.89 7.7C14.9826 7.60742 15.0925 7.53398 15.2135 7.48387C15.3344 7.43377 15.4641 7.40798 15.595 7.40798C15.7259 7.40798 15.8556 7.43377 15.9765 7.48387C16.0975 7.53398 16.2074 7.60742 16.3 7.7C16.3926 7.79258 16.466 7.90249 16.5161 8.02346C16.5662 8.14442 16.592 8.27407 16.592 8.405C16.592 8.53593 16.5662 8.66558 16.5161 8.78654C16.466 8.90751 16.3926 9.01742 16.3 9.11L13.41 12L16.3 14.89C16.68 15.27 16.68 15.91 16.3 16.3Z" fill="#33445C"/>
                    </svg>
                  </button>
                </div>
              {:else}
                <div class="flex items-center justify-between w-full rounded-lg p-2 bg-white text-[#66768B] mt-2">{bookCodeAndName.split(/, (.*)/s)[1]}</div>
              {/if}
            {/each}
          </div>
        </div>
      {/if}
    {:else}
      <div class="rounded-lg p-6 bg-[#e5e8eb] text-[#66768B]">Selections will appear here once a book is selected</div>
    {/if}
    {#if !resourceTypeRegExp.test($location) && $resourceTypesCountStore > 0}
      <div class="flex items-center justify-between my-2">
        <div class="flex items-center justify-between">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 2C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2H6ZM6 4H13V9H18V20H6V4ZM8 12V14H16V12H8ZM8 16V18H13V16H8Z" fill="#001533"/>
          </svg>
          <h2 class="ml-2 font-semibold text-xl text-[#33445C]">Resource</h2>
        </div>
        <button class="flex bg-white text-[#33445c] hover:bg-[#efefef] py-2 px-4 rounded" on:click={() => push("/v2/resource_types")}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 17.4624V20.5024C3 20.7824 3.22 21.0024 3.5 21.0024H6.54C6.67 21.0024 6.8 20.9524 6.89 20.8524L17.81 9.94244L14.06 6.19244L3.15 17.1024C3.05 17.2024 3 17.3224 3 17.4624ZM20.71 7.04244C20.8027 6.94993 20.8762 6.84004 20.9264 6.71907C20.9766 6.59809 21.0024 6.46841 21.0024 6.33744C21.0024 6.20648 20.9766 6.07679 20.9264 5.95582C20.8762 5.83485 20.8027 5.72496 20.71 5.63244L18.37 3.29244C18.2775 3.19974 18.1676 3.12619 18.0466 3.07601C17.9257 3.02583 17.796 3 17.665 3C17.534 3 17.4043 3.02583 17.2834 3.07601C17.1624 3.12619 17.0525 3.19974 16.96 3.29244L15.13 5.12244L18.88 8.87244L20.71 7.04244Z" fill="#33445C"/>
          </svg>
          Edit
        </button>
      </div>
    {:else}
      <div class="flex items-center my-2">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M6 2C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2H6ZM6 4H13V9H18V20H6V4ZM8 12V14H16V12H8ZM8 16V18H13V16H8Z" fill="#001533"/>
        </svg>
        <h2 class="ml-2 font-semibold text-xl text-[#33445C]">Resource</h2>
      </div>
    {/if}
    {#if $resourceTypesCountStore > 0}
      {#each $lang0ResourceTypesStore as resourceTypeCodeAndName}
        {#if resourceTypeRegExp.test($location)}
          <div class="inline-flex items-center justify-between w-full rounded-lg p-4 bg-white text-[#66768B] mt-2">{resourceTypeCodeAndName.split(/, (.*)/s)[1]}
            <button on:click={() => uncheckLang0ResourceType(resourceTypeCodeAndName)}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.47 2 2 6.47 2 12C2 17.53 6.47 22 12 22C17.53 22 22 17.53 22 12C22 6.47 17.53 2 12 2ZM16.3 16.3C16.2075 16.3927 16.0976 16.4663 15.9766 16.5164C15.8557 16.5666 15.726 16.5924 15.595 16.5924C15.464 16.5924 15.3343 16.5666 15.2134 16.5164C15.0924 16.4663 14.9825 16.3927 14.89 16.3L12 13.41L9.11 16.3C8.92302 16.487 8.66943 16.592 8.405 16.592C8.14057 16.592 7.88698 16.487 7.7 16.3C7.51302 16.113 7.40798 15.8594 7.40798 15.595C7.40798 15.4641 7.43377 15.3344 7.48387 15.2135C7.53398 15.0925 7.60742 14.9826 7.7 14.89L10.59 12L7.7 9.11C7.51302 8.92302 7.40798 8.66943 7.40798 8.405C7.40798 8.14057 7.51302 7.88698 7.7 7.7C7.88698 7.51302 8.14057 7.40798 8.405 7.40798C8.66943 7.40798 8.92302 7.51302 9.11 7.7L12 10.59L14.89 7.7C14.9826 7.60742 15.0925 7.53398 15.2135 7.48387C15.3344 7.43377 15.4641 7.40798 15.595 7.40798C15.7259 7.40798 15.8556 7.43377 15.9765 7.48387C16.0975 7.53398 16.2074 7.60742 16.3 7.7C16.3926 7.79258 16.466 7.90249 16.5161 8.02346C16.5662 8.14442 16.592 8.27407 16.592 8.405C16.592 8.53593 16.5662 8.66558 16.5161 8.78654C16.466 8.90751 16.3926 9.01742 16.3 9.11L13.41 12L16.3 14.89C16.68 15.27 16.68 15.91 16.3 16.3Z" fill="#33445C"/>
              </svg>
            </button>
          </div>
        {:else}
          <div class="inline-flex items-center justify-between w-full rounded-lg p-4 bg-white text-[#66768B] mt-2">{resourceTypeCodeAndName.split(/, (.*)/s)[1]}</div>
        {/if}
      {/each}
      {#each $lang1ResourceTypesStore as resourceTypeCodeAndName}
        {#if resourceTypeRegExp.test($location)}
          <div class="flex items-center justify-between w-full rounded-lg p-4 bg-white text-[#66768B] mt-2">{resourceTypeCodeAndName.split(/, (.*)/s)[1]}
            <button on:click={() => uncheckLang1ResourceType(resourceTypeCodeAndName)}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.47 2 2 6.47 2 12C2 17.53 6.47 22 12 22C17.53 22 22 17.53 22 12C22 6.47 17.53 2 12 2ZM16.3 16.3C16.2075 16.3927 16.0976 16.4663 15.9766 16.5164C15.8557 16.5666 15.726 16.5924 15.595 16.5924C15.464 16.5924 15.3343 16.5666 15.2134 16.5164C15.0924 16.4663 14.9825 16.3927 14.89 16.3L12 13.41L9.11 16.3C8.92302 16.487 8.66943 16.592 8.405 16.592C8.14057 16.592 7.88698 16.487 7.7 16.3C7.51302 16.113 7.40798 15.8594 7.40798 15.595C7.40798 15.4641 7.43377 15.3344 7.48387 15.2135C7.53398 15.0925 7.60742 14.9826 7.7 14.89L10.59 12L7.7 9.11C7.51302 8.92302 7.40798 8.66943 7.40798 8.405C7.40798 8.14057 7.51302 7.88698 7.7 7.7C7.88698 7.51302 8.14057 7.40798 8.405 7.40798C8.66943 7.40798 8.92302 7.51302 9.11 7.7L12 10.59L14.89 7.7C14.9826 7.60742 15.0925 7.53398 15.2135 7.48387C15.3344 7.43377 15.4641 7.40798 15.595 7.40798C15.7259 7.40798 15.8556 7.43377 15.9765 7.48387C16.0975 7.53398 16.2074 7.60742 16.3 7.7C16.3926 7.79258 16.466 7.90249 16.5161 8.02346C16.5662 8.14442 16.592 8.27407 16.592 8.405C16.592 8.53593 16.5662 8.66558 16.5161 8.78654C16.466 8.90751 16.3926 9.01742 16.3 9.11L13.41 12L16.3 14.89C16.68 15.27 16.68 15.91 16.3 16.3Z" fill="#33445C"/>
              </svg>
            </button>
          </div>
        {:else}
          <div class="flex items-center justify-between w-full rounded-lg p-4 bg-white text-[#66768B] mt-2">{resourceTypeCodeAndName.split(/, (.*)/s)[1]}</div>
        {/if}
      {/each}
    {:else}
      <div class="rounded-lg p-6 bg-[#e5e8eb] text-[#66768b]">Selections will appear here once a resource is selected</div>
    {/if}
  </div>
