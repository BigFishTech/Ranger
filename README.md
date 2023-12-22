# Standalone 4g Smart Speaker

### Summary: 
Almost all the information you consume out of your screen can be represented as text, and LLMs are now smart enough to bridge that gap. Whether its getting answer to a question, texting, calling, entertainment like music and podcast, or even a social media feed like twitter, it can all be represented as text and be interfaced with through a voice assistant. You can essentially do everything your phone can with just voice commands now. So, we should have a device that let's you leave the screen behind! A small battery powered smart speaker that can survive in any environment and gives you instant access to a voice based AI with the push of a button. 

### Goal: 
Open Ai is funding AI startups, winners get 1 million dollars, you must enter by January 26. Our goal is to create a simple prototype that exemplifies the main features for creating a sick ass demo video before the deadline. https://www.openai.fund/news/converge-2

### Requirements for the prototype: 
• Battery powered
• 4g (Hologram io data plan)
• Audio in / audio out
• Low latency Ai chat
• Custom water resistant housing
• Intelligent Ai that we can converse with in the demo vid

### Prototype Part List
* Raspi 4b: $55
    * https://www.adafruit.com/product/4296
* 4g SIM7600A-H HAT: $72
    * https://www.amazon.com/dp/B07PLTP3M6?psc=1&smid=A2SA28G0M1VPHD&ref_=chk_typ_imgToDp
* SIM card: $5 (Can get first one for free)
    * https://store.hologram.io/products/hyper-euicc-iot-sim-card
* Pi juice power supply: $90 (With shipping)
    * https://uk.pi-supply.com/products/pijuice-standard
* Adafruit Mic array: $25
    * https://www.digikey.com/en/products/detail/adafruit-industries-llc/4757/13536263
* Waterproof speaker
* Camera: $20
    * https://www.amazon.com/Arducam-Raspberry-Megapixel-Compatible-RPI-CAM-8MP/dp/B09V576TFN/ref=sr_1_10
* SD card
* Programmable nice push buttons
* Volume buttons
* RGB LED Strip
* Custom Waterproof Housing


# The Software
The software is currently broken up into four areas:
• Firmware (Python on the RPI)
• Firebase Cloud Functions (Our Backend)
• Flutter App (Our Frontend)
• Firebase Hosting (Vercel Website): We'll eventually need this to market and sell the product, as well as this is where we will need process payments so we can get around those fucked 30% cuts Apple and Google take for IAPs. 

### Firmware
Python code that runs the hardware, responsible for everything on the device but especially the main feature the the user presses the talk button, starts speaking, presses the button again and the device communicates with our backend, receives the ai voice response back and plays it through the device speakers. 

### Firebase Cloud Functions
This is where we will put the main function that the raspberry pi calls, where it sends voice data in, the cloud function processes with speech to text, creates a chatgpt response, turns it back into voice with text to speech, then streams that data back to the rpi device. 

### Flutter App
This is where the user manages everything, can change the AI personality, change the voice, see chat history, select different tools the AI can use, etc.

### Firebase Hosting
Vercel website, will set up eventually


# Business Model
This is way up to change, but considering the costs, it probably makes sense to do something like break even on the physical device sale but charge a monthly fee that accounts for data plan and api usage and try to make money there. 

### Costs
• The physical device
• The 4g data plan
• API usage, OpenAI STT, TSS, GPT, and Firebase backend


# Fun Thoughts
• Use camera for taking pictures as well as feeding pictures into the AI as prompts

