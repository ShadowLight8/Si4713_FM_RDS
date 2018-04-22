<?php $outputGPIOReset = "";
if (isset($_POST["GPIOResetButton"]))
{
$outputGPIOReset = shell_exec(escapeshellcmd("sudo ".$pluginDirectory."/".$_GET['plugin']."/callbacks.py --reset"));
}
?>

<script type="text/javascript">
<!--
    function toggle(id) {
       var e = document.getElementById(id);
       if(e.style.display == 'block')
          e.style.display = 'none';
       else
          e.style.display = 'block';
    }
//-->
</script>

<div id="Si4713detection" class="settings">
<fieldset>
<legend>Si4713 Detection</legend>

<div style="float: right; clear: right;">
<span style="float: right;"><a href="#" onclick="toggle('RPi_Pinout')">Click for Raspberry Pi GPIO#'s</a></span>
<a title="By Tux-Man (Own work) [CC0], via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File%3ARaspberry_Pi_Mle_B_-_GPIO.png">
<img id="RPi_Pinout" style="display: none" width="333" alt="Raspberry Pi Mle B - GPIO" src="https://upload.wikimedia.org/wikipedia/commons/f/fd/Raspberry_Pi_Mle_B_-_GPIO.png"/>
</a>
</div>

<?php exec("sudo i2cget -y 1 0x63", $output, $return_val); ?>
<p>Detecting Si4713:
<?php if (implode($output) != "Error: Read failed") : ?>
<span class='good'>Detected on I<sup>2</sup>C address 0x63</span>
<?php else: ?>
<span class='bad'>Not detected on I<sup>2</sup>C addresses 0x63</span> <!-- TODO: Check on 0x11 as well -->
<br />
The Si4713 must be reset after power on to be detected. Set the GPIO# for the reset pin, save, use the GPIO Reset, and restart FPP.
<?php endif; ?>
</p>
<p>GPIO# (not pin number) for Reset: <?php PrintSettingText("GPIONumReset", 1, 0, 2, 2, "Si4713_FM_RDS", "4"); ?><?php PrintSettingSave("GPIONumReset", "GPIONumReset", 1, 0, "Si4713_FM_RDS"); ?></p>
<form method="post"><p><button name="GPIOResetButton">Execute GPIO Reset</button> <?php echo $outputGPIOReset; ?></p></form>
</fieldset>
</div>

<br />

<div id="Si4713Pluginsettings" class="settings">
<fieldset>
<legend>Si4713 Plugin Settings</legend>
<p>Start Si4713 at: <?php PrintSettingSelect("Start", "Start", 1, 0, "FPPDStart", Array("FPPD Start (default)"=>"FPPDStart", "Playlist Start"=>"PlaylistStart", "Never"=>"Never"), "Si4713_FM_RDS", ""); ?><br />
At Start, the Si4713 is reset, FM settings initialized, will broadcast any audio played, and send static RDS messages (if enabled).</p>
<p>Stop Si4713 at: <?php PrintSettingSelect("Stop", "Stop", 1, 0, "Never", Array("Playlist Stop"=>"PlaylistStop", "Never (default)"=>"Never"), "Si4713_FM_RDS", ""); ?><br />
At Stop, the Si4713 is reset. Listeners will hear static.</p>
</fieldset>
</div>

<br />

<div id="Si4713FMsettings" class="settings">
<fieldset>
<legend>Si4713 FM Settings</legend>
<p>Frequency (76.00-108.00): <?php PrintSettingText("Frequency", 1, 0, 6, 6, "Si4713_FM_RDS", "100.10"); ?>MHz <?php PrintSettingSave("Frequency", "Frequency", 1, 0, "Si4713_FM_RDS"); ?></p>
<p>Power (88-115, 116-120<sup>*</sup>): <?php PrintSettingText("Power", 1, 0, 3, 3, "Si4713_FM_RDS", "95"); ?>dB&mu;V <?php PrintSettingSave("Power", "Power", 1, 0, "Si4713_FM_RDS"); ?>
<br /><sup>*</sup>Can be set as high as 120dB&mu;V, but voltage accuracy above 115dB&mu;V is not guaranteed.</p>
<p>Preemphasis: <?php PrintSettingSelect("Preemphasis", "Preemphasis", 1, 0, "75us", Array("50&mu;s (Europe, Australia, Japan)"=>"50us", "75&mu;s (USA, default)"=>"75us"), "Si4713_FM_RDS", ""); ?></p>
<p>Antenna Tuning Capacitor (0=Auto, 1-191): <?php PrintSettingText("AntCap", 1, 0, 3, 3, "Si4713_FM_RDS", "0"); ?> * 0.25pF <?php PrintSettingSave("AntCap", "AntCap", 1, 0, "Si4713_FM_RDS"); ?></p>
</fieldset>
</div>

<br />

<div id="Si4713RDSsettings" class="settings">
<fieldset>
<legend>Si4713 RDS Settings</legend>
<p>Enable RDS: <?php PrintSettingCheckbox("EnableRDS", "EnableRDS", 1, 0, "True", "False", "Si4713_FM_RDS", ""); ?></p>
<p>RDS Station - Sent 8 characters at a time</p>
<p>Delay between 8 character blocks (&gt;=3): <?php PrintSettingText("StationDelay", 1, 0, 3, 3, "Si4713_FM_RDS", "4"); ?>seconds <?php PrintSettingSave("StationDelay", "StationDelay", 1, 0, "Si4713_FM_RDS"); ?></p>
<table style="border: 1px solid black; border-collapse: collapse; text-align: center">
<tr>
<th style="border: 1px solid black; padding: 5px">Static Text (can be blank)</th>
<th style="border: 1px solid black; padding: 5px">Show Title</th>
<th style="border: 1px solid black; padding: 5px">Show Artist</th>
<th style="border: 1px solid black; padding: 5px" colspan="3">Track Number</th>
</tr>
<tr>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingText("StationText", 1, 0, 64, 32, "Si4713_FM_RDS", "Happy   Hallo-     -ween"); ?></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingCheckbox("StationTitle", "StationTitle", 1, 0, "True", "False", "Si4713_FM_RDS", ""); ?></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingCheckbox("StationArtist", "StationArtist", 1, 0, "True", "False", "Si4713_FM_RDS", ""); ?></td>
<td style="border: 1px solid black; border-style: none solid">Prefix</td>
<td style="border: 1px solid black; border-style: none solid">Show</td>
<td style="border: 1px solid black; border-style: none solid">Suffix</td>
</tr>
<tr>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingSave("StationText", "StationText", 1, 0, "Si4713_FM_RDS"); ?></td>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingText("StationTrackNumPre", 1, 0, 64, 8, "Si4713_FM_RDS", ""); ?></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingCheckbox("StationTrackNum", "StationTrackNum", 1, 0, "True", "False", "Si4713_FM_RDS", ""); ?></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingText("StationTrackNumSuf", 1, 0, 64, 8, "Si4713_FM_RDS", "of 4"); ?></td>
</tr>
<tr>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingSave("StationTrackNumPre", "StationTrackNumPre", 1, 0, "Si4713_FM_RDS"); ?></td>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingSave("StationTrackNumSuf", "StationTrackNumSuf", 1, 0, "Si4713_FM_RDS"); ?></td>
</tr>
</table>

<br />

<p>RDS Text - Sent 32 characters at a time</p>
<p>Delay between 32 character blocks (&gt;=3): <?php PrintSettingText("RDSTextDelay", 1, 0, 3, 3, "Si4713_FM_RDS", "7"); ?>seconds <?php PrintSettingSave("RDSTestDelay", "RDSTextDelay", 1, 0, "Si4713_FM_RDS"); ?></p>
<table style="border: 1px solid black; border-collapse: collapse; text-align: center">
<tr>
<th style="border: 1px solid black; padding: 5px">Static Text (can be blank)</th>
<th style="border: 1px solid black; padding: 5px">Show Title</th>
<th style="border: 1px solid black; padding: 5px">Show Artist</th>
<th style="border: 1px solid black; padding: 5px" colspan="3">Track Number</th>
</tr>
<tr>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingText("RDSTextText", 1, 0, 64, 32, "Si4713_FM_RDS", "Happy   Hallo-     -ween"); ?></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingCheckbox("RDSTextTitle", "RDSTextTitle", 1, 0, "True", "False", "Si4713_FM_RDS", ""); ?></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingCheckbox("RDSTextArtist", "RDSTextArtist", 1, 0, "True", "False", "Si4713_FM_RDS", ""); ?></td>
<td style="border: 1px solid black; border-style: none solid">Prefix</td>
<td style="border: 1px solid black; border-style: none solid">Show</td>
<td style="border: 1px solid black; border-style: none solid">Suffix</td>
</tr>
<tr>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingSave("RDSTextText", "RDSTextText", 1, 0, "Si4713_FM_RDS"); ?></td>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingText("RDSTextTrackNumPre", 1, 0, 64, 8, "Si4713_FM_RDS", ""); ?></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingCheckbox("RDSTextTrackNum", "RDSTextTrackNum", 1, 0, "True", "False", "Si4713_FM_RDS", ""); ?></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingText("RDSTextTrackNumSuf", 1, 0, 64, 8, "Si4713_FM_RDS", "of 4"); ?></td>
</tr>
<tr>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingSave("RDSTextTrackNumPre", "RDSTextTrackNumPre", 1, 0, "Si4713_FM_RDS"); ?></td>
<td style="border: 1px solid black; border-style: none solid"></td>
<td style="border: 1px solid black; border-style: none solid"><?php PrintSettingSave("RDSTextTrackNumSuf", "RDSTextTrackNumSuf", 1, 0, "Si4713_FM_RDS"); ?></td>
</tr>
</table>
</fieldset>
</div>

<br />

<div id="Si4713Debug" class="settings">
<fieldset>
<legend>Si4713 Debugging</legend>
<p>Si4713_callbacks.log: <input onclick= "ViewFile('Logs', '../plugins/Si4713_FM_RDS/Si4713_callbacks.log');" id="btnViewScript" class="buttons" type="button" value="View" /></p>
<p>Si4713_updater.log: <input onclick= "ViewFile('Logs', '../plugins/Si4713_FM_RDS/Si4713_updater.log');" id="btnViewScript" class="buttons" type="button" value="View" /></p>
</fieldset>
</div>

<div id='fileViewer' title='File Viewer' style="display: none">
  <div id='fileText'>
  </div>
</div>

<br />

<div id="Si4713Info" class="settings">
<fieldset>
<legend>Additional Si4713 Information</legend>
<p>Physical connection from Pi -&gt; Si4713<br />
Pin 3 (SDA1) -&gt; SDA<br />
Pin 4 (+5v) -&gt; Vin<br />
Pin 5 (SCL1) -&gt; SCL<br />
Pin 6 (GND) -&gt; GND<br />
Pin 7 (GPIO4) -&gt; RST<br />
USB sound card and a short audio cable to go from the Pi to the Si4713</p>
<p><a href="https://www.adafruit.com/product/1958">Adafruit Si4713 Breakout Board</a></p>
<p><a href="https://www.silabs.com/documents/public/data-sheets/Si4712-13-B30.pdf">Si4713 Datasheet</a></p>
<p><a href="https://www.silabs.com/documents/public/application-notes/AN332.pdf">Si4713 Programming Guide</a></p>
<p><a href="https://www.silabs.com/documents/public/user-guides/Si47xxEVB.pdf">Si4713 Evaluation Board Guide</a></p>
</fieldset>
<!-- last div intentionally skipped to fix footer background -->
