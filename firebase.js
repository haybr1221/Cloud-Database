const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "movie-database-d9ec9.firebaseapp.com",
    projectId: "movie-database-d9ec9",
    storageBucket: "movie-database-d9ec9.appspot.com",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID",
    databaseURL: "YOUR_DATABASE_URL"
  };
  
  const app = firebase.initializeApp(firebaseConfig);
  const db = firebase.firestore();
  