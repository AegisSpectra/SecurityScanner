use std::ffi::{CStr, c_char};

#[no_mangle]
pub extern "C" fn calculate_threat_score(input: *const c_char) -> i32 {
    let c_str = unsafe { CStr::from_ptr(input) };
    let description = c_str.to_str().unwrap_or_default().to_lowercase();

    if description.contains("malware") {
        95
    } else if description.contains("suspicious") {
        60
    } else if description.contains("high cpu") {
        45
    } else if description.contains("risk") {
        75
    } else {
        20
    }
}
