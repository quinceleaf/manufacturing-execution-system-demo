// Alpine.js for sidebar
const setup = () => {
  return {
    isSidebarOpen: false,
    toggleSidebarMenu() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    isSidebarPinned: false,
    toggleSidebarPin() {
      this.isSidebarPinned = !this.isSidebarPinned;
      this.setPinChoice();
    },
    setPinChoice() {
      url = document.querySelector('#settings').dataset.toggleSidebarPinUrl;
      fetch(url, {
        method: 'GET',
      })
      .then(res => res.json())
      .then(data => {
        console.log(data)
      });
    },
  };
}
setup();