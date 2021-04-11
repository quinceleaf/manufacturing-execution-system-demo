// Alpine.js for header
const setup = () => {
  return {
    isMessageOpen: false,
    toggleMessageMenu() {
      this.isMessageOpen = !this.isMessageOpen;
    },

    isSettingsOpen: false,
    toggleSettingsMenu() {
      this.isSettingsOpen = !this.isSettingsOpen;
    },

    isProfileOpen: false,
    toggleProfileMenu() {
      this.isProfileOpen = !this.isProfileOpen;
    },
  };
}
setup();