<script lang="ts">
  import { ntBookStore, otBookStore } from '$lib/stores/BooksStore'
  import { getCode, getName } from '$lib/utils'

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
      <div class="flex items-center py-2 pl-4">
        <input
          id="select-all-old-testament"
          type="checkbox"
          class="checkbox-target checkbox-style"
          on:change={(event) => selectAllOtBookCodes(event)}
        />
        <label for="select-all-old-testament" class="pl-1 text-xl text-[#33445C]">Select all</label>
      </div>
    {/if}
    {#if otBookCodes?.length > 0}
      {#each otBookCodes as bookCodeAndName, index}
        <label for="bookcode-ot-{index}">
          <div
            class="target py-2 pl-4"
            style={filteredOtBookCodes.includes(bookCodeAndName) ? '' : 'display: none'}
          >
            <div class="target2 flex items-center justify-between">
              <div class="target3 flex items-center">
                <input
                  id="bookcode-ot-{index}"
                  type="checkbox"
                  bind:group={$otBookStore}
                  value={bookCodeAndName}
                  class="checkbox-target checkbox-style"
                />
                <span class="pl-1 text-xl text-[#33445C]">{getName(bookCodeAndName)}</span>
              </div>
            </div>
            <div class="ml-6 text-xl text-[#33445C]">{getCode(bookCodeAndName)}</div>
          </div>
        </label>
      {/each}
    {/if}
  {:else}
    {#if ntBookCodes?.length > 0}
      <div class="flex items-center py-2 pl-4">
        <input
          id="select-all-new-testament"
          type="checkbox"
          class="checkbox-target checkbox-style"
          on:change={(event) => selectAllNtBookCodes(event)}
        />
        <label
          for="select-all-new-testament"
          class="pl-1
                                                     text-xl text-[#33445C]">Select all</label
        >
      </div>
    {/if}
    {#if ntBookCodes?.length > 0}
      {#each ntBookCodes as bookCodeAndName, index}
        <label for="bookcode-nt-{index}">
          <div
            class="target py-2 pl-4"
            style={filteredNtBookCodes.includes(bookCodeAndName) ? '' : 'display: none'}
          >
            <div class="target2 flex items-center justify-between">
              <div class="target3 flex items-center">
                <input
                  id="bookcode-nt-{index}"
                  type="checkbox"
                  bind:group={$ntBookStore}
                  value={bookCodeAndName}
                  class="checkbox-target checkbox-style"
                />
                <span class="pl-1 text-xl text-[#33445C]">{getName(bookCodeAndName)}</span>
              </div>
            </div>
            <div class="ml-6 text-xl text-[#33445C]">{getCode(bookCodeAndName)}</div>
          </div>
        </label>
      {/each}
    {/if}
  {/if}
</main>
