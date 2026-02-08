//borrow
const menuItems = [
  { label: 'About', link: 'winter_penguin_page.html', icon: 'images/applicationIconBg.png' },
  { label: 'Resume', link: 'index.html', icon: 'images/resumeIcon.png' },
  { label: 'Chatbot', link: 'chatbot.html', icon: 'images/chatbotIcon.png' },
];

const socialItems = [
  { label: 'Instagram', link: 'https://instagram.com' },
  { label: 'LinkedIn - Rahul Anand', link: 'https://linkedin.com' },
  { label: 'LinkedIn - Bruce Ma', link: 'https://linkedin.com' }
];

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
<div style={{ height: '4.75vh', background: 'rgba(26, 26, 26, 0)' }}>
  <StaggeredMenu
    position="left"
    items={menuItems}
    socialItems={socialItems}
    displaySocials={false} // change this to true if I decide to link social media on the navbar
    displayItemNumbering={false}
    menuButtonColor="#fff"
    openMenuButtonColor="#fff"
    changeMenuColorOnOpen={true}
    colors={['#113360', '#fbfbfbff']}
    accentColor="#113360"
    onMenuOpen={() => document.body.classList.add('sidebar-open')}
    onMenuClose={() => document.body.classList.remove('sidebar-open')}
  />
</div>
);