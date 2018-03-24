<div id="Si4713detection" class="settings">
<fieldset>
<legend>Si4713 Detection</legend>
<?php exec("sudo i2cget -y 1 99", $output, $return_val); ?>

<p>
Detecting Si4713:
<?php if (implode($output) == "0x80") : ?>
<span class='good'>Detected on I2C address 0x63</span>
<?php else: ?>
<span class='bad'>Not detected on I2C addresses 0x63 or 0x11</span>
<br />
The Si4713 must be reset after power on to be detected. Update the GPIO Reset Pin below and try again.
<?php endif; ?>
</p>
<p>GPIO Reset Pin #: <?php PrintSettingText("GPIOResetPin", 1, 0, 2, 2, "Si4713_FM_RDS", "4"); ?><?php PrintSettingSave("GPIOResetPin", "GPIOResetPin", 1, 0, "Si4713_FM_RDS"); ?></p>
</fieldset>
</div>

<br />

<?php if (function_exists('PrintSettingSave')): ?>

<div id="Si4713FMsettings" class="settings">
<fieldset>
<legend>Si4713 FM Settings</legend>

<p>Frequency (7600 - 10800): <?php PrintSettingText("Frequency", 1, 0, 5, 5, "Si4713_FM_RDS"); ?>MHz <?php PrintSettingSave("Frequency", "Frequency", 1, 0, "Si4713_FM_RDS"); ?></p>
<p>Power (88-115)*: <?php PrintSettingText("Power", 1, 0, 3, 3, "Si4713_FM_RDS", "90"); ?>dB&mu;V <?php PrintSettingSave("Power", "Power", 1, 0, "Si4713_FM_RDS"); ?></p>
<p>* Can be set as high as 120dB&mu;V, but voltage accuracy above 115dB&mu;V is not guaranteed.
<p>Pre-emphasis: <?php PrintSettingSelect("Pre-emphasis", "Pre-emphasis", 1, 0, "75us", Array("50&mu;s (Europe, Australia, Japan)"=>"50us", "75&mu;s (USA, default)"=>"75us"), "Si4713_FM_RDS", ""); ?></p>
<p>(Audio limiter and compression, maybe a separate section)</p>
</fieldset>
</div>

<br />

<div id="Si4713RDSsettings" class="settings">
<fieldset>
<legend>Si4713 RDS Settings</legend>
</fieldset>
</div>

<br />

<div id="plugininfo" class="settings">
<fieldset>
<legend>Plugin Information</legend>
<p>Instructions
<ul>
<li>Setup transmitter and save to EEPROM, or click the "Toggle transmitter
with playlist" option above.</li>
<li>Change audio on "FPP Settings" page.  Go to the FPP Settings screen and
select the Vast as your sound output instead of the Pi's built-in audio.</li>
<li>Tag your MP3s/OGG files appropriate.  The tags are used to set the Artist
and Title fields for RDS's RT+ text. The rest will happen auto-magically!</li>
</ul>
</p>

<?php else: ?>

<div id="rds" class="settings">
<fieldset>
<legend>RDS Support Instructions</legend>

<p style="color: red;">You're running an old version of FPP that doesn't yet contain the required
helper functions needed by this plugin. Advanced features are disabled.</p>

<p>You must first set up your Vast V-FMT212R using the Vast Electronics
software and save it to the EEPROM.  Once you have your VAST setup to transmit
on your frequency when booted, you can plug it into the Raspberry Pi and
reboot.  You will then go to the FPP Settings screen and select the Vast as
your sound output instead of the Pi's built-in audio.</p>

<?php endif; ?>

<p>Known Issues:
<ul>
<li>VastFMT will "crash" and be unable to receive RDS data if not used with
a powered USB hub.  If this happens, the transmitter must be unplugged and re-
plugged into the Pi - <a target="_new"
href="https://github.com/Materdaddy/fpp-vastfmt/issues/2">Bug 2</a></li>
</ul>

Planned Features:
<ul>
<li>Saving settings to EEPROM.</li>
</ul>

<p>To report a bug, please file it against the fpp-vastfmt plugin project here:
<a href="https://github.com/Materdaddy/fpp-vastfmt/issues/new" target="_new">fpp-vastfmt GitHub Issues</a></p>

</fieldset>
</div>
<br />
