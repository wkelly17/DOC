<script lang="ts">
  import active from 'svelte-spa-router/active'
</script>

<div class="bg-secondary">
  <div class="flex justify-center border-b border-gray-200 dark:border-gray-700">
    <a
      class="h-10 px-4 py-2 -mb-px text-sm text-center bg-transparent border-b-2 sm:text-base whitespace-nowrap"
      use:active={{
        className:
          'border-primary text-primary dark:border-primary-400 dark:text-primary-300',
        inactiveClassName:
          'border-transparent text-gray-700 dark:text-white hover:border-gray-400 cursor-base'
      }}
      href="#/"
    >
      Content
    </a>
    <!-- <a -->
    <!--   class="h-10 px-4 py-2 -mb-px text-sm text-center bg-transparent border-b-2 sm:text-base whitespace-nowrap" -->
    <!--   use:active={{ -->
    <!--     className: -->
    <!--       'border-primary text-primary dark:border-primary-400 dark:text-primary-300', -->
    <!--     inactiveClassName: -->
    <!--       'border-transparent text-gray-700 dark:text-white hover:border-gray-400 cursor-base' -->
    <!--   }} -->
    <!--   href="#/settings" -->
    <!-- > -->
    <!--   Settings -->
    <!-- </a> -->
    <a
      class="h-10 px-4 py-2 -mb-px text-sm text-center bg-transparent border-b-2 sm:text-base whitespace-nowrap"
      use:active={{
        className:
          'border-primary text-primary dark:border-primary-400 dark:text-primary-300',
        inactiveClassName:
          'border-transparent text-gray-700 dark:text-white hover:border-gray-400 cursor-base'
      }}
      href="#/about"
    >
      About
    </a>
  </div>
</div>

<!-- <div class="bg-secondary"> -->
<!--   <div class="flex justify-center"> -->
<!--     <div class="tabs"> -->
<!--       <a -->
<!--         href="#/" -->
<!--         use:active={{ className: 'tab-active text-primary' }} -->
<!--         class="tab tab-bordered">Content</a -->
<!--       > -->
<!--       <a -->
<!--         href="#/settings" -->
<!--         use:active={{ className: 'tab-active text-primary' }} -->
<!--         class="tab tab-bordered">Settings</a -->
<!--       > -->
<!--       <a -->
<!--         href="#/about" -->
<!--         use:active={{ className: 'tab-active text-primary' }} -->
<!--         class="tab tab-bordered">About</a -->
<!--       > -->
<!--     </div> -->
<!--   </div> -->
<!-- </div> -->
