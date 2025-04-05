'use strict';

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";
import { getFirestore, doc, setDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-firestore.js";  // Import Firestore

const firebaseConfig = {

  apiKey: "AIzaSyCyBd_5kFklz8jmkVyzOVUhHvSbcv4rSMI",

  authDomain: "task-management-1a4b0.firebaseapp.com",

  projectId: "task-management-1a4b0",

  storageBucket: "task-management-1a4b0.firebasestorage.app",

  messagingSenderId: "1072199463288",

  appId: "1:1072199463288:web:9444ae547e7c80649f988d",

  measurementId: "G-PBD0Y8TVXB"

};





const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app); 
window.addEventListener('load', (e) => {
  e.preventDefault();
   if (window.location.pathname === '/') {
    document.getElementById("login").addEventListener('click',async function (e) {
     const errorLabel=document.querySelector('.error');

      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      e.preventDefault();
      try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
    
        sessionStorage.setItem('email',user.email);
        const token = await user.getIdToken(true);
    
        document.cookie = `token=${token};path=/;SameSite=Strict`;
        errorLabel.innerText="Wait we are trying to login....."
        setTimeout(() => {
          
          window.location.href = "/index";
        }, 1000);
      } catch (error) {
        errorLabel.innerText=error
        console.error("Error during login:", error);
      }
    });
  }

  else if (window.location.pathname === '/register') {
  
    document.getElementById("signup").addEventListener('click', function (e) {
      const name = document.getElementById('name').value;
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      
      e.preventDefault();
      createUserWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      const user = userCredential.user;

      // Save user details to Firestore
      setDoc(doc(db, 'users', user.uid), {
        name: name,
        email: email,
        createdAt: serverTimestamp()  // Set server timestamp
      })
      .then(() => {
        user.getIdToken().then((token) => {
          document.cookie = "token=" + token + ";path=/;SameSite=Strict";
          window.location.href = "/index";
        });
      })
      .catch((error) => {
        console.log('Error saving user details to Firestore:', error);
      });
    })
    .catch((error) => {
      console.log('Error creating user:', error);
    });
    });
  }

});


