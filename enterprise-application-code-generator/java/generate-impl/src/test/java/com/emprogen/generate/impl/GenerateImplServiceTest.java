package com.emprogen.generate.impl;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.emprogen.generate.impl.GenerateImplService;

public class GenerateImplServiceTest {

    public static final Logger LOGGER = LoggerFactory.getLogger(GenerateImplServiceTest.class.getName());

    public List<String> typeField = new ArrayList<>();

    public Map<String, String> testMethod(final String a, Set<String> b) throws NullPointerException, RuntimeException {
        return null;
    }

    @Test
    public void test() {
        testField();
        testMethod();
        testModifiers();

        String impl = GenerateImplService.generateClass("com.github.mshin.jaxrms.rs.api.JaxrmsService",
                "com.github.mshin.generate.impl");
        System.out.println(impl);

    }
    public static void testModifiers() {
        Method[] methods = null;
        try {
            methods = GenerateImplServiceTest.class.getMethods();
        } catch (SecurityException e) {
            LOGGER.error(e.getClass().getName(), e);
        }
        for (Method m : methods) {
            int mod = m.getModifiers();
            LOGGER.info("mod: " + mod);
            LOGGER.info("isAbstract: " + Modifier.isAbstract(mod));
            
            Modifier.isAbstract(mod);
            Modifier.toString(m.getModifiers());
        }
    }
    public static void testMethod() {
        Method[] methods = null;
        try {
            methods = GenerateImplServiceTest.class.getMethods();
        } catch (SecurityException e) {
            LOGGER.error(e.getClass().getName(), e);
        }
        for (Method m : methods) {
            String methodS = GenerateImplService.createMethodString(m);
            // System.out.println(Modifier.toString(m.getModifiers()));
            LOGGER.info(methodS);
        }

    }

    public static void testField() {
        Field testField = null;
        try {
            testField = GenerateImplServiceTest.class.getField("typeField");
        } catch (NoSuchFieldException e) {
            LOGGER.error(e.getClass().getName(), e);
        } catch (SecurityException e) {
            LOGGER.error(e.getClass().getName(), e);
        }
        Type type = testField.getGenericType();
        String typeString = type.getTypeName();
        LOGGER.info(typeString);
    }

}