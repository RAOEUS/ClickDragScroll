; ============================
; ========= SETTINGS =========
; ============================

; Button to initiate drag-to-scroll mode.
; Options: "RButton", "MButton"
InitiateDragButton := "MButton"

; Speed settings
SlowSpeedFactor := 10 ; Increase for slower minimum speed, decrease for faster minimum speed
AccelerationFactor := 1.2 ; Increase for more acceleration effect, decrease for less

; Fractional threshold for smoother scrolling at slow speeds
; Smaller value makes scroll more sensitive to small mouse movements
FractionalThreshold := 0.8

; Delay (in milliseconds) before drag-to-scroll mode is activated after holding the right mouse button
DragActivationDelay := 200

; List of applications to exclude from drag-to-scroll
;ExclusionList := ["Notepad", "Your Game Title", "Another App Title"]
ExclusionList := []

; Toggle Mode: true to enable, false to disable
ToggleMode := false
; Hotkey to activate toggle mode
ToggleModeHotkey := "^!t" ; Default to Ctrl + Alt + T

; Reverse Scrolling: true to enable, false to disable
ReverseScrolling := false

; ============================
; ========== START ===========
; ============================

#Persistent
#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%

Dragging := false
ActiveMode := false
xInit := 0
yInit := 0

; Dynamically set the hotkeys based on the setting
Hotkey, %InitiateDragButton%, InitiateDragCheck
Hotkey, %InitiateDragButton% Up, InitiateDragStop
Hotkey, %ToggleModeHotkey%, ToggleDragToScroll
return 

ToggleDragToScroll:
  ToggleMode := !ToggleMode
  if (ToggleMode) {
    MouseGetPos, xInit, yInit
    ActiveMode := true
    SetTimer, CheckMouseMove, 10
  } else {
    ActiveMode := false
    SetTimer, CheckMouseMove, Off
  }
return

InitiateDragCheck:
  if (ToggleMode) {
    return
  }

  ; Check if the current window title is in the exclusion list
  WinGetTitle, CurrentTitle, A
  for index, title in ExclusionList {
    if (InStr(CurrentTitle, title) > 0) {
      return
    }
  }

  MouseGetPos, xInit, yInit
  ; Set a timer to check if the button has been held down for more than the activation delay
  SetTimer, InitiateDrag, %DragActivationDelay%
return

InitiateDrag:
  SetTimer, InitiateDrag, Off ; Turn off this timer
  Dragging := true
  ActiveMode := true
  SetTimer, CheckMouseMove, 10 ; Start the movement check timer
return

; Detect mouse button up
InitiateDragStop:
  SetTimer, InitiateDrag, Off ; Turn off the initiation timer
  if (Dragging) {
    Dragging := false
    ActiveMode := ToggleMode
    SetTimer, CheckMouseMove, Off
    Tooltip ; Hide tooltip
    return ; Prevent default click action
  } else {
    ; If not dragging, send an input to simulate a normal click based on the InitiateDragButton setting
    if (InitiateDragButton = "MButton") {
      Click, Middle
    } else if (InitiateDragButton = "RButton"){
      Click, Right
    }
  }
return

; Variables to accumulate scrolling amounts
accumulatedY := 0
accumulatedX := 0

CheckMouseMove:
  if (!ActiveMode) {
    return
  }

  MouseGetPos, xCur, yCur
  xDelta := xCur - xInit
  yDelta := yCur - yInit

  ; Calculate dynamic scroll speed based on cursor movement with configurable sensitivity
  scrollSpeedY := (Abs(yDelta) / SlowSpeedFactor) ** AccelerationFactor
  scrollSpeedX := (Abs(xDelta) / SlowSpeedFactor) ** AccelerationFactor

  ; Accumulate the scroll amounts
  accumulatedY += scrollSpeedY
  accumulatedX += scrollSpeedX

  if (xDelta != 0 or yDelta != 0) {
    if (ReverseScrolling) {
      yDelta := -yDelta
      xDelta := -xDelta
    } 

    ; Send wheel events based on the accumulated scroll amount using the fractional threshold
    while (accumulatedY >= FractionalThreshold) {
      if (yDelta > 0) {
        Click, WheelDown
      } else {
        Click, WheelUp
      }
      accumulatedY -= FractionalThreshold
    }

    Send, {Shift Down}
    while (accumulatedX >= FractionalThreshold) {
      if (xDelta > 0) {
        Click, WheelDown
      } else {
        Click, WheelUp
      }
      accumulatedX -= FractionalThreshold
    }
    Send, {Shift Up}

    ; Reset the mouse to the initial position
    MouseMove, %xInit%, %yInit%, 0
  }
return