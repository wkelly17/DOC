import { writable } from 'svelte/store'

// constructor function
const createStore = () => {
  // initialize internal writable store with empty list
  const { subscribe, set, update } = writable<string[]>([])

  // mark message as read by removing it from the list
  function remove(book: string) {
    update(books => books.filter(bk => bk !== book))
  }

  // add new message to the top of the list
  function add(book: string) {
    update(currentBooks => {
      console.log(`currentBooks: ${currentBooks}`)
      // Only add a book if it isn't already in the store.
      if (
        !currentBooks.map(resourceCodeAndName => resourceCodeAndName[0]).includes(book[0])
      ) {
        console.log(`Adding book: ${book}`)
        return [book, ...currentBooks]
      } else {
        console.log(`Book: ${book} is already in store`)
        return currentBooks
      }
    })
  }

  return {
    subscribe,
    add,
    init: set, // alias set method to init
    remove,
    clear: () => set([])
  }
}

// initialize the store
const bookStore = createStore()

export { bookStore }
