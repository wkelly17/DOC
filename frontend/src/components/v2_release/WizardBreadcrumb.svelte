<script lang="ts">
  import { location } from 'svelte-spa-router'
  import { push } from 'svelte-spa-router'
  import {langCountStore} from '../../stores/v2_release/LanguagesStore'
  import {bookCountStore} from '../../stores/v2_release/BooksStore'
  import {resourceTypesCountStore} from '../../stores/v2_release/ResourceTypesStore'
  import { resetStores } from '../../lib/utils'
  import { resetValuesStore } from '../../stores/v2_release/NotificationStore'

  let langRegExp = new RegExp('.*languages.*')
  let bookRegExp = new RegExp('.*books.*')
  let resourceTypeRegExp = new RegExp('.*resource_types.*')


  function submitLanguages() {
    // If books store or resource types store are not empty, then we
    // should reset them when we change the languages.
    if ($bookCountStore > 0 || $resourceTypesCountStore > 0) {
      resetValuesStore.set(true)
    }
    resetStores('books')
    resetStores('resource_types')
    resetStores('settings')
    resetStores('notifications')
    push('#/v2/books')
  }

  function submitBooks() {
    // If resource types store is not empty, then we
    // should reset it when we change books.
    if ($resourceTypesCountStore > 0) {
      resetValuesStore.set(true)
    }
    resetStores('resource_types')
    resetStores('settings')
    resetStores('notifications')
    push('#/v2/resource_types')
  }

  function submitResourceTypes() {
    resetStores('settings')
    resetStores('notifications')
    push('#/v2/settings')
  }
</script>

<!-- wizard breadcrumb -->
<div class="p-4 border border-[#E5E8EB]">
  <div
    class="flex items-center justify-between text-[#B3B9C2] leading-8 text-xl font-semibold"
  >
    <button class="btn">
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M18.0374 10.5166H7.28489L11.9825 5.69276C12.3579 5.30724 12.3579 4.6746 11.9825 4.28908C11.8934 4.19744 11.7877 4.12474 11.6712 4.07514C11.5547 4.02553 11.4299 4 11.3038 4C11.1778 4 11.0529 4.02553 10.9365 4.07514C10.82 4.12474 10.7142 4.19744 10.6252 4.28908L4.28151 10.8033C4.19227 10.8948 4.12148 11.0034 4.07317 11.123C4.02486 11.2426 4 11.3707 4 11.5002C4 11.6297 4.02486 11.7579 4.07317 11.8774C4.12148 11.997 4.19227 12.1057 4.28151 12.1971L10.6252 18.7113C10.7143 18.8029 10.8201 18.8755 10.9366 18.925C11.053 18.9745 11.1778 19 11.3038 19C11.4299 19 11.5547 18.9745 11.6711 18.925C11.7876 18.8755 11.8934 18.8029 11.9825 18.7113C12.0716 18.6198 12.1423 18.5112 12.1905 18.3916C12.2388 18.272 12.2636 18.1439 12.2636 18.0144C12.2636 17.885 12.2388 17.7569 12.1905 17.6373C12.1423 17.5177 12.0716 17.4091 11.9825 17.3175L7.28489 12.4937H18.0374C18.5668 12.4937 19 12.0488 19 11.5052C19 10.9615 18.5668 10.5166 18.0374 10.5166Z"
          fill="#33445C"
        /></svg
      >Back
    </button>
    <div class="inline-flex items-center">
      <div class="avatar placeholder">
        {#if langRegExp.test($location)}
        <div class="bg-neutral-focus text-neutral-content rounded-full w-8 bg-[#015ad9]">
          <span class="text-xs text-white">1</span>
        </div>
        {:else}
        <div class="bg-neutral-focus text-neutral-content rounded-full w-8 bg-[#b3b9c2]">
          <span class="text-xs text-white">1</span>
        </div>
        {/if}
      </div>
      <span class="ml-2">Languages</span>
    </div>
    <div class="inline-flex items-center">
      <div class="avatar placeholder">
        {#if bookRegExp.test($location)}
        <div class="bg-neutral-focus text-neutral-content rounded-full w-8 bg-[#015ad9]">
          <span class="text-xs text-white">2</span>
        </div>
        {:else}
        <div class="bg-neutral-focus text-neutral-content rounded-full w-8 bg-[#b3b9c2]">
          <span class="text-xs text-white">2</span>
        </div>
        {/if}
      </div>
      <span class="ml-2">Books</span>
    </div>
    <div class="inline-flex items-center">
      <div class="avatar placeholder">
        {#if resourceTypeRegExp.test($location)}
        <div class="bg-neutral-focus text-neutral-content rounded-full w-8 bg-[#015ad9]">
          <span class="text-xs text-white">3</span>
        </div>
        {:else}
        <div class="bg-neutral-focus text-neutral-content rounded-full w-8 bg-[#b3b9c2]">
          <span class="text-xs text-white">3</span>
        </div>
        {/if}
      </div>
      <span class="ml-2">Resources</span>
    </div>
    <div class="inline-flex items-center">
      <div class="avatar placeholder">
        <div class="bg-neutral-focus text-neutral-content rounded-full w-8 bg-[#b3b9c2]">
          <span class="text-xs text-white">4</span>
        </div>
      </div>
      <span class="ml-2">Review</span>
    </div>
  {#if langRegExp.test($location) && $langCountStore > 0}
    <button class="btn btn-primary"
            on:click={() => submitLanguages()}>
      Next
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        >
        <path
          d="M4.96262 12.4876H15.7151L11.0175 17.3083C10.6421 17.6936 10.6421 18.3258 11.0175 18.7111C11.3929 19.0963 11.9994 19.0963 12.3748 18.7111L18.7185 12.2011C18.8077 12.1097 18.8785 12.0012 18.9268 11.8817C18.9751 11.7622 19 11.6341 19 11.5047C19 11.3753 18.9751 11.2472 18.9268 11.1277C18.8785 11.0082 18.8077 10.8997 18.7185 10.8083L12.3844 4.28847C12.2953 4.19701 12.1895 4.12447 12.0731 4.07497C11.9566 4.02548 11.8318 4 11.7058 4C11.5798 4 11.4549 4.02548 11.3385 4.07497C11.2221 4.12447 11.1163 4.19701 11.0271 4.28847C10.938 4.37993 10.8673 4.4885 10.8191 4.608C10.7709 4.72749 10.746 4.85557 10.746 4.98491C10.746 5.11424 10.7709 5.24232 10.8191 5.36181C10.8673 5.48131 10.938 5.58988 11.0271 5.68134L15.7151 10.5119H4.96262C4.43318 10.5119 4 10.9564 4 11.4998C4 12.0431 4.43318 12.4876 4.96262 12.4876Z"
          fill="#001533"
          />
      </svg>
    </button>
  {:else if bookRegExp.test($location) && $bookCountStore > 0}
    <button class="btn btn-primary"
            on:click={() => submitBooks()}>
      Next
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        >
        <path
          d="M4.96262 12.4876H15.7151L11.0175 17.3083C10.6421 17.6936 10.6421 18.3258 11.0175 18.7111C11.3929 19.0963 11.9994 19.0963 12.3748 18.7111L18.7185 12.2011C18.8077 12.1097 18.8785 12.0012 18.9268 11.8817C18.9751 11.7622 19 11.6341 19 11.5047C19 11.3753 18.9751 11.2472 18.9268 11.1277C18.8785 11.0082 18.8077 10.8997 18.7185 10.8083L12.3844 4.28847C12.2953 4.19701 12.1895 4.12447 12.0731 4.07497C11.9566 4.02548 11.8318 4 11.7058 4C11.5798 4 11.4549 4.02548 11.3385 4.07497C11.2221 4.12447 11.1163 4.19701 11.0271 4.28847C10.938 4.37993 10.8673 4.4885 10.8191 4.608C10.7709 4.72749 10.746 4.85557 10.746 4.98491C10.746 5.11424 10.7709 5.24232 10.8191 5.36181C10.8673 5.48131 10.938 5.58988 11.0271 5.68134L15.7151 10.5119H4.96262C4.43318 10.5119 4 10.9564 4 11.4998C4 12.0431 4.43318 12.4876 4.96262 12.4876Z"
          fill="#001533"
          />
      </svg>
    </button>
  {:else if resourceTypeRegExp.test($location) && $resourceTypesCountStore > 0}
    <button class="btn btn-primary"
            on:click={() => submitResourceTypes()}>
      Next
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        >
        <path
          d="M4.96262 12.4876H15.7151L11.0175 17.3083C10.6421 17.6936 10.6421 18.3258 11.0175 18.7111C11.3929 19.0963 11.9994 19.0963 12.3748 18.7111L18.7185 12.2011C18.8077 12.1097 18.8785 12.0012 18.9268 11.8817C18.9751 11.7622 19 11.6341 19 11.5047C19 11.3753 18.9751 11.2472 18.9268 11.1277C18.8785 11.0082 18.8077 10.8997 18.7185 10.8083L12.3844 4.28847C12.2953 4.19701 12.1895 4.12447 12.0731 4.07497C11.9566 4.02548 11.8318 4 11.7058 4C11.5798 4 11.4549 4.02548 11.3385 4.07497C11.2221 4.12447 11.1163 4.19701 11.0271 4.28847C10.938 4.37993 10.8673 4.4885 10.8191 4.608C10.7709 4.72749 10.746 4.85557 10.746 4.98491C10.746 5.11424 10.7709 5.24232 10.8191 5.36181C10.8673 5.48131 10.938 5.58988 11.0271 5.68134L15.7151 10.5119H4.96262C4.43318 10.5119 4 10.9564 4 11.4998C4 12.0431 4.43318 12.4876 4.96262 12.4876Z"
          fill="#001533"
          />
      </svg>
    </button>
  {:else}
    <!-- {#if langRegExp.test($location) && $langCountStore === 0 || bookRegExp.test($location) && bookCountStore === 0 || -->
    <!-- resourceTypeRegExp.test($location) && $resourceTypesCountStore === 0} -->
    <button class="btn">
      Next
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        >
        <path
          d="M4.96262 12.4876H15.7151L11.0175 17.3083C10.6421 17.6936 10.6421 18.3258 11.0175 18.7111C11.3929 19.0963 11.9994 19.0963 12.3748 18.7111L18.7185 12.2011C18.8077 12.1097 18.8785 12.0012 18.9268 11.8817C18.9751 11.7622 19 11.6341 19 11.5047C19 11.3753 18.9751 11.2472 18.9268 11.1277C18.8785 11.0082 18.8077 10.8997 18.7185 10.8083L12.3844 4.28847C12.2953 4.19701 12.1895 4.12447 12.0731 4.07497C11.9566 4.02548 11.8318 4 11.7058 4C11.5798 4 11.4549 4.02548 11.3385 4.07497C11.2221 4.12447 11.1163 4.19701 11.0271 4.28847C10.938 4.37993 10.8673 4.4885 10.8191 4.608C10.7709 4.72749 10.746 4.85557 10.746 4.98491C10.746 5.11424 10.7709 5.24232 10.8191 5.36181C10.8673 5.48131 10.938 5.58988 11.0271 5.68134L15.7151 10.5119H4.96262C4.43318 10.5119 4 10.9564 4 11.4998C4 12.0431 4.43318 12.4876 4.96262 12.4876Z"
          fill="#001533"
          />
      </svg>
    </button>
  {/if}
  </div>
</div>
