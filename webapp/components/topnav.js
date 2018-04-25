import preact from 'preact';
import linkState from 'linkstate';


export default ({nav, toggleNav}) => (<div class="pure-menu pure-menu-horizontal">
  <a class="pure-menu-heading pure-menu-link" onClick={e => {e.preventDefault(); toggleNav('home');}}>passfoo</a>

  <ul class="pure-menu-list">
    <li class="pure-menu-item">
      <a class="pure-menu-link" onClick={e => {e.preventDefault(); toggleNav('questions');}}>Questions</a>
    </li>

    <li class="pure-menu-item">
      <a class="pure-menu-link" onClick={e => {e.preventDefault(); toggleNav('passwords');}}>Passwords</a>
    </li>

    <li class="pure-menu-item">
      <a class="pure-menu-link" onClick={e => {e.preventDefault(); toggleNav('about');}}>About</a>
    </li>
  </ul>
</div>);
