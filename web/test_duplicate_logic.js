// 重复匹配检测逻辑测试
class TestConfigurationManager {
    constructor() {
        this.labelToChannelMap = new Map();
        this.channelToLabelMap = new Map();
        this.duplicateMatches = [];
    }

    addLabelConfiguration(channelId, labelId) {
        // 检查是否有重复匹配（在设置新映射之前）
        this.checkDuplicateMatches(channelId, labelId);
        
        // 设置映射关系
        this.labelToChannelMap.set(labelId, channelId);
        this.channelToLabelMap.set(channelId, labelId);
    }

    removeLabelConfiguration(channelId) {
        const labelId = this.channelToLabelMap.get(channelId);
        if (labelId) {
            this.labelToChannelMap.delete(labelId);
        }
        this.channelToLabelMap.delete(channelId);
    }

    checkDuplicateMatches(channelId, labelId) {
        this.duplicateMatches = [];
        
        // None是特殊选项，不参与重复匹配检测
        if (labelId === 'no_match') {
            return;
        }
        
        const channelType = this.getChannelType(channelId);
        
        // 检查是否有其他通道已经使用了相同的标签
        const existingChannel = this.labelToChannelMap.get(labelId);
        if (existingChannel && existingChannel !== channelId) {
            // 检查是否是相同类型的通道
            const existingChannelType = this.getChannelType(existingChannel);
            if (existingChannelType === channelType) {
                this.duplicateMatches.push({
                    labelId: labelId,
                    channel1: existingChannel,
                    channel2: channelId,
                    channelType: channelType
                });
            }
        }
    }

    getChannelType(channelId) {
        if (channelId.startsWith('T') || channelId.startsWith('TRC') || channelId.startsWith('temp')) {
            return 'temperature';
        }
        if (channelId.startsWith('P') || channelId.startsWith('pressure')) {
            return 'pressure';
        }
        if (channelId.startsWith('at') || channelId.startsWith('environment')) {
            return 'environment';
        }
        if (channelId.startsWith('p') || channelId.startsWith('power')) {
            return 'power';
        }
        return 'other';
    }

    hasDuplicateMatches() {
        return this.duplicateMatches.length > 0;
    }

    getDuplicateMatches() {
        return this.duplicateMatches;
    }

    reset() {
        this.labelToChannelMap.clear();
        this.channelToLabelMap.clear();
        this.duplicateMatches = [];
    }
}

// 测试函数
function runTests() {
    console.log('=== 重复匹配检测测试 ===\n');

    // 测试1: 同类型重复匹配检测
    console.log('测试1: 同类型重复匹配检测');
    const config1 = new TestConfigurationManager();
    config1.addLabelConfiguration('T1', 'TRC');
    config1.addLabelConfiguration('T2', 'TRC');
    
    if (config1.hasDuplicateMatches()) {
        const duplicates = config1.getDuplicateMatches();
        console.log('✅ 测试通过！检测到重复匹配:');
        console.log(`   标签 "TRC" 在${duplicates[0].channelType}类型中被多个通道使用`);
        console.log(`   通道1: ${duplicates[0].channel1}`);
        console.log(`   通道2: ${duplicates[0].channel2}`);
    } else {
        console.log('❌ 测试失败！应该检测到重复匹配但没有检测到');
    }
    console.log('');

    // 测试2: 跨类型不检测
    console.log('测试2: 跨类型不检测');
    const config2 = new TestConfigurationManager();
    config2.addLabelConfiguration('T1', 'TRC');  // temperature类型
    config2.addLabelConfiguration('P1', 'TRC');  // pressure类型
    
    if (config2.hasDuplicateMatches()) {
        console.log('❌ 测试失败！跨类型不应该检测到重复匹配');
    } else {
        console.log('✅ 测试通过！跨类型不检测重复匹配');
        console.log('   T1 -> TRC (temperature类型)');
        console.log('   P1 -> TRC (pressure类型)');
    }
    console.log('');

    // 测试3: 正常配置
    console.log('测试3: 正常配置');
    const config3 = new TestConfigurationManager();
    config3.addLabelConfiguration('T1', 'TRC');
    config3.addLabelConfiguration('T2', 'TEMP');
    config3.addLabelConfiguration('P1', 'pressure');
    config3.addLabelConfiguration('P2', 'None');
    
    if (config3.hasDuplicateMatches()) {
        console.log('❌ 测试失败！正常配置不应该有重复匹配');
    } else {
        console.log('✅ 测试通过！正常配置没有重复匹配');
        console.log('   T1 -> TRC');
        console.log('   T2 -> TEMP');
        console.log('   P1 -> pressure');
        console.log('   P2 -> None');
    }
    console.log('');

    // 测试4: 通道类型分类
    console.log('测试4: 通道类型分类');
    const config4 = new TestConfigurationManager();
    const testCases = [
        { channel: 'T1', expected: 'temperature' },
        { channel: 'TRC1', expected: 'temperature' },
        { channel: 'temp1', expected: 'temperature' },
        { channel: 'P1', expected: 'pressure' },
        { channel: 'pressure1', expected: 'pressure' },
        { channel: 'at1', expected: 'environment' },
        { channel: 'environment1', expected: 'environment' },
        { channel: 'p1', expected: 'power' },
        { channel: 'power1', expected: 'power' },
        { channel: 'other1', expected: 'other' }
    ];
    
    let allPassed = true;
    testCases.forEach(testCase => {
        const actual = config4.getChannelType(testCase.channel);
        const passed = actual === testCase.expected;
        console.log(`${testCase.channel}: ${passed ? '✅' : '❌'} (期望: ${testCase.expected}, 实际: ${actual})`);
        if (!passed) allPassed = false;
    });
    
    console.log(allPassed ? '✅ 所有通道类型分类测试通过！' : '❌ 部分通道类型分类测试失败！');
    console.log('');

    // 测试5: 复杂场景
    console.log('测试5: 复杂场景');
    const config5 = new TestConfigurationManager();
    config5.addLabelConfiguration('T1', 'TRC');
    config5.addLabelConfiguration('T2', 'TEMP');
    config5.addLabelConfiguration('P1', 'pressure');
    config5.addLabelConfiguration('P2', 'pressure');  // 重复匹配
    
    if (config5.hasDuplicateMatches()) {
        const duplicates = config5.getDuplicateMatches();
        console.log('✅ 测试通过！检测到重复匹配:');
        duplicates.forEach(dup => {
            console.log(`   标签 "${dup.labelId}" 在${dup.channelType}类型中被多个通道使用`);
        });
    } else {
        console.log('❌ 测试失败！应该检测到重复匹配但没有检测到');
    }
    console.log('');

    // 测试6: None选项特殊处理
    console.log('测试6: None选项特殊处理');
    const config6 = new TestConfigurationManager();
    config6.addLabelConfiguration('T1', 'TRC');
    config6.addLabelConfiguration('T2', 'no_match');  // None选项
    config6.addLabelConfiguration('T3', 'no_match');  // 多个None选项
    
    if (config6.hasDuplicateMatches()) {
        console.log('❌ 测试失败！None选项不应该被检测为重复匹配');
    } else {
        console.log('✅ 测试通过！None选项被正确处理');
        console.log('   T1 -> TRC');
        console.log('   T2 -> None');
        console.log('   T3 -> None (多个None选项不冲突)');
    }
    console.log('');

    // 测试7: None与普通标签混合
    console.log('测试7: None与普通标签混合');
    const config7 = new TestConfigurationManager();
    config7.addLabelConfiguration('T1', 'TRC');
    config7.addLabelConfiguration('T2', 'no_match');
    config7.addLabelConfiguration('P1', 'pressure');
    config7.addLabelConfiguration('P2', 'no_match');
    config7.addLabelConfiguration('T3', 'TRC');  // 重复匹配
    
    if (config7.hasDuplicateMatches()) {
        const duplicates = config7.getDuplicateMatches();
        console.log('✅ 测试通过！检测到重复匹配:');
        duplicates.forEach(dup => {
            console.log(`   标签 "${dup.labelId}" 在${dup.channelType}类型中被多个通道使用`);
        });
    } else {
        console.log('❌ 测试失败！应该检测到重复匹配但没有检测到');
    }
}

// 运行测试
if (typeof window === 'undefined') {
    // Node.js环境
    runTests();
} else {
    // 浏览器环境
    window.runTests = runTests;
    console.log('测试已加载，请在浏览器控制台中运行 runTests() 来执行测试');
} 