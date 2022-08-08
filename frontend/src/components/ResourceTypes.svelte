<script lang="ts">
  import { bookStore } from '../stores/BooksStore'
</script>

<ul>
  {#each $bookStore as book}
    <li>{book}</li>
  {/each}
</ul>
