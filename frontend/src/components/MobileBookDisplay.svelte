<script lang="ts">
  import { ntBookStore, otBookStore } from '../stores/BooksStore'
  import { getCode, getName } from '../lib/utils'

  export let showOldTestament: boolean
  export let otBookCodes: Array<string>
  export let ntBookCodes: Array<string>
  export let filteredOtBookCodes: Array<string>
  export let filteredNtBookCodes: Array<string>

  function selectAllOtBookCodes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      $otBookStore = otBookCodes
    } else {
      $otBookStore = []
    }
  }

  function selectAllNtBookCodes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      $ntBookStore = ntBookCodes
    } else {
      $ntBookStore = []
    }
  }
</script>

<main class="flex-1 overflow-y-auto p-4">
  {#if showOldTestament}
    {#if otBookCodes?.length > 0}
      <div class="flex items-center pl-4 py-2">
        <input
          id="select-all-old-testament"
          type="checkbox"
          class="checkbox checkbox-dark-bordered"
          on:change={event => selectAllOtBookCodes(event)}
        />
        <label for="select-all-old-testament" class="text-[#33445C] pl-1"
          >Select all</label
        >
      </div>
    {/if}
    {#if otBookCodes?.length > 0}
      {#each otBookCodes as bookCodeAndName, index}
        <div class="pl-4 py-2 target">
          <div
            class="flex items-center justify-between target2"
            style={filteredOtBookCodes.includes(bookCodeAndName) ? '' : 'display: none'}
          >
            <div class="flex items-center target3">
              <input
                id="bookcode-ot-{index}"
                type="checkbox"
                bind:group={$otBookStore}
                value={bookCodeAndName}
                class="checkbox checkbox-dark-bordered"
              />
              <label for="bookcode-ot-{index}" class="text-[#33445C] pl-1"
                >{getName(bookCodeAndName)}</label
              >
            </div>
          </div>
          <div class="ml-6 text-[#33445C]">{getCode(bookCodeAndName)}</div>
        </div>
      {/each}
    {/if}
  {:else}
    {#if ntBookCodes?.length > 0}
      <div class="flex items-center pl-4 py-2">
        <input
          id="select-all-new-testament"
          type="checkbox"
          class="checkbox checkbox-dark-bordered"
          on:change={event => selectAllNtBookCodes(event)}
        />
        <label for="select-all-new-testament" class="text-[#33445C] pl-1"
          >Select all</label
        >
      </div>
    {/if}
    {#if ntBookCodes?.length > 0}
      {#each ntBookCodes as bookCodeAndName, index}
        <div class="pl-4 py-2 target">
          <div
            class="flex items-center justify-between target2"
            style={filteredNtBookCodes.includes(bookCodeAndName) ? '' : 'display: none'}
          >
            <div class="flex items-center target3">
              <input
                id="bookcode-nt-{index}"
                type="checkbox"
                bind:group={$ntBookStore}
                value={bookCodeAndName}
                class="checkbox checkbox-dark-bordered"
              />
              <label for="bookcode-nt-{index}" class="text-[#33445C] pl-1"
                >{getName(bookCodeAndName)}</label
              >
            </div>
          </div>
          <div class="ml-6 text-[#33445C]">{getCode(bookCodeAndName)}</div>
        </div>
      {/each}
    {/if}
  {/if}
</main>
