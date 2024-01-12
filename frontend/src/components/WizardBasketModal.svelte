<script lang="ts">
  export let showWizardBasketModal = false
  export let title = ''
  let dialog: HTMLDialogElement

  $: if (dialog && showWizardBasketModal) dialog.showModal()
</script>

<!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
<dialog
  bind:this={dialog}
  on:close={() => (showWizardBasketModal = false)}
  on:click|self={() => dialog.close()}
  id="dialog-container"
  class="fixed z-50 h-full w-full overflow-y-auto overflow-x-hidden outline-none rounded-lg bg-[#f2f3f5]"
  tabindex="-1"
>
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div
    on:click|stopPropagation
    class="pointer-events-none relative mx-auto my-6 w-auto max-w-lg sm:h-[calc(100%-3rem)]"
  >
    <div
      class="pointer-events-auto relative flex w-full max-h-full
                flex-col overflow-y-auto border-none bg-[#f2f3f5] text-current outline-none"
    >
      <div
        class="flex flex-shrink-0 items-center justify-between bg-[#f2f3f5] border-b border-[#e5e8eb] p-4"
      >
        <h5 class="text-xl font-bold text-[#33445C]">{title}</h5>
        <button autofocus on:click={() => dialog.close()}>
          <svg
            class="ml-2"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2C6.47 2 2 6.47 2 12C2 17.53 6.47 22 12 22C17.53 22 22 17.53 22 12C22 6.47 17.53 2 12 2ZM16.3 16.3C16.2075 16.3927 16.0976 16.4663 15.9766 16.5164C15.8557 16.5666 15.726 16.5924 15.595 16.5924C15.464 16.5924 15.3343 16.5666 15.2134 16.5164C15.0924 16.4663 14.9825 16.3927 14.89 16.3L12 13.41L9.11 16.3C8.92302 16.487 8.66943 16.592 8.405 16.592C8.14057 16.592 7.88698 16.487 7.7 16.3C7.51302 16.113 7.40798 15.8594 7.40798 15.595C7.40798 15.4641 7.43377 15.3344 7.48387 15.2135C7.53398 15.0925 7.60742 14.9826 7.7 14.89L10.59 12L7.7 9.11C7.51302 8.92302 7.40798 8.66943 7.40798 8.405C7.40798 8.14057 7.51302 7.88698 7.7 7.7C7.88698 7.51302 8.14057 7.40798 8.405 7.40798C8.66943 7.40798 8.92302 7.51302 9.11 7.7L12 10.59L14.89 7.7C14.9826 7.60742 15.0925 7.53398 15.2135 7.48387C15.3344 7.43377 15.4641 7.40798 15.595 7.40798C15.7259 7.40798 15.8556 7.43377 15.9765 7.48387C16.0975 7.53398 16.2074 7.60742 16.3 7.7C16.3926 7.79258 16.466 7.90249 16.5161 8.02346C16.5662 8.14442 16.592 8.27407 16.592 8.405C16.592 8.53593 16.5662 8.66558 16.5161 8.78654C16.466 8.90751 16.3926 9.01742 16.3 9.11L13.41 12L16.3 14.89C16.68 15.27 16.68 15.91 16.3 16.3Z"
              fill="#33445C"
            />
          </svg>
        </button>
      </div>
      <div class="relative flex-auto overflow-y-auto">
        <slot name="body" />
      </div>
      <div class="flex flex-shrink-0 flex-wrap items-center order-t border-[#e5e8eb] p-4">
        <!-- svelte-ignore a11y-autofocus -->
        <button
          class="h-[48px] w-[115px] rounded-md border-2
                       border-[#e5e8eb] bg-white font-medium
                       leading-tight text-[#33445C] text-xl transition
                       duration-150 ease-in-out"
          on:click={() => dialog.close()}
        >
          <div class="flex items-center">
            <svg
              class="ml-2"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M12 2C6.47 2 2 6.47 2 12C2 17.53 6.47 22 12 22C17.53 22 22 17.53 22 12C22 6.47 17.53 2 12 2ZM16.3 16.3C16.2075 16.3927 16.0976 16.4663 15.9766 16.5164C15.8557 16.5666 15.726 16.5924 15.595 16.5924C15.464 16.5924 15.3343 16.5666 15.2134 16.5164C15.0924 16.4663 14.9825 16.3927 14.89 16.3L12 13.41L9.11 16.3C8.92302 16.487 8.66943 16.592 8.405 16.592C8.14057 16.592 7.88698 16.487 7.7 16.3C7.51302 16.113 7.40798 15.8594 7.40798 15.595C7.40798 15.4641 7.43377 15.3344 7.48387 15.2135C7.53398 15.0925 7.60742 14.9826 7.7 14.89L10.59 12L7.7 9.11C7.51302 8.92302 7.40798 8.66943 7.40798 8.405C7.40798 8.14057 7.51302 7.88698 7.7 7.7C7.88698 7.51302 8.14057 7.40798 8.405 7.40798C8.66943 7.40798 8.92302 7.51302 9.11 7.7L12 10.59L14.89 7.7C14.9826 7.60742 15.0925 7.53398 15.2135 7.48387C15.3344 7.43377 15.4641 7.40798 15.595 7.40798C15.7259 7.40798 15.8556 7.43377 15.9765 7.48387C16.0975 7.53398 16.2074 7.60742 16.3 7.7C16.3926 7.79258 16.466 7.90249 16.5161 8.02346C16.5662 8.14442 16.592 8.27407 16.592 8.405C16.592 8.53593 16.5662 8.66558 16.5161 8.78654C16.466 8.90751 16.3926 9.01742 16.3 9.11L13.41 12L16.3 14.89C16.68 15.27 16.68 15.91 16.3 16.3Z"
                fill="#33445C"
              />
            </svg>
            <span class="ml-2">Close</span>
          </div>
        </button>
      </div>
    </div>
  </div>
</dialog>

<style>
  #dialog-container {
    box-shadow: 0px 6px 6px 0px #0015333b;

    box-shadow: 0px 10px 20px 0px #00153330;
  }
</style>
