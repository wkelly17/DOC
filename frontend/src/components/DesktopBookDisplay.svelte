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
      <div class="flex items-center h-[56px] px-4">
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
        <label for="bookcode-ot-{index}">
          <div
            class="flex items-center justify-between target h-[56px] px-4"
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
              <span class="text-[#33445C] pl-1">{getName(bookCodeAndName)}</span>
            </div>
            <span class="text-[#33445C]">{getCode(bookCodeAndName)}</span>
          </div>
        </label>
      {/each}
    {/if}
  {:else}
    {#if ntBookCodes?.length > 0}
      <div class="flex items-center h-[56px] px-4">
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
        <label for="bookcode-nt-{index}">
          <div
            class="flex items-center justify-between target h-[56px] px-4"
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
              <span class="text-[#33445C] pl-1">{getName(bookCodeAndName)}</span>
            </div>
            <span class="text-[#33445C]">{getCode(bookCodeAndName)}</span>
          </div>
        </label>
      {/each}
    {/if}
  {/if}
</main>
